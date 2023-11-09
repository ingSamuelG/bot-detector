from logHelper import logHelper
import redis
import os
import socket
import paramiko
import re
import json
from datetime import timedelta


class botDetector:
    def __init__(self):
        REDIS_HOST = os.getenv("REDIS_HOST")
        REDIS_PORT = os.getenv("REDIS_PORT")
        REDIS_PASS = os.getenv("REDIS_PASS")
        self.max_req_per_min = os.getenv("MAX_REQUEST_PER_MIN")

        self.cache = redis.StrictRedis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=0,
            decode_responses=True,
            password=REDIS_PASS,
        )

        self.logHelper = logHelper()

    def __get_total_lines_from_cache(self):
        try:
            val = self.cache.get("total_lines")
            if val:
                print(f"Found: this {val}")
                return int(val)
            else:
                print("Not found in cache")
                total = self.logHelper.get_total_lines_for_prod_log()
                self.cache.setex("total_lines", 1, total)
                return int(total)
        except socket.gaierror as e:
            print(f"Error on the SSH in the log helper: the address is incorrect: {e}")
        except paramiko.ssh_exception.AuthenticationException as e:
            print(
                f"Error on the SSH in the log helper: the password or user is incorrect: {e}"
            )
        except redis.exceptions.ConnectionError as e:
            print(f"Redis its not aviable {e}")

    def __set_last_processed_line_to_cache(self, line_number):
        print("setting last line to cache")
        self.cache.set("last_processed_line", line_number)

    def __get_last_processed_line_to_cache(self):
        return self.cache.get("last_processed_line")

    def __set_last_bad_ip_dic_cache(self, dic):
        json_for_redis = json.dumps(dic)
        self.cache.set("last_bad_ip_dic", json_for_redis)

    def __last_bad_ip_dic_cache(self):
        redis_dic = self.cache.get("last_bad_ip_dic")
        return json.loads(redis_dic)

    def __set_dom_for_ip_cache(self, ip, dom):
        self.cache.setex(ip, 21600, dom)

    def ___get_dom_for_ip_cache(self, ip):
        self.cache.get(ip)

    def __get_dom(self, ip):
        cache_dom = self.___get_dom_for_ip_cache(ip)
        if cache_dom:
            return cache_dom
        else:
            bytes_out = self.logHelper.ssh_server_con.exec_comand_in_server_get_stdout(
                f"host {ip}"
            )
            dom_string = bytes_out.decode("utf-8").split(" ")[-1]
            self.__set_dom_for_ip_cache(ip, dom_string)
            return dom_string

    def __remove_good_bots(self, bad_ip_dic):
        good_bot_list = [
            "search.msn.com",
            "yandex.com",
            "googlebot.com",
            "google.com",
            "googleusercontent.com",
        ]

        for date_time_key, ips in bad_ip_dic.items():
            # for ip, amount_of_req in ips.items():
            for ip in list(ips.keys()):
                dom_for_ip = self.__get_dom(ip)
                is_a_good_bot = any(
                    [
                        True if good_bot in dom_for_ip else False
                        for good_bot in good_bot_list
                    ]
                )

                # print(
                #     f"{('3(NXDOMAIN)' in dom_for_ip)}  and this is dom {dom_for_ip} \n"
                # )
                bad_ip_dic[date_time_key][ip]["dom"] = dom_for_ip

                if is_a_good_bot:
                    bad_ip_dic[date_time_key].pop(ip)

        return bad_ip_dic

    def __verify_domain(self, domain):
        pass

    def __get_bad_ips_by_num_req_per_min(self, log_data):
        bad_ips = []
        date_ip_per_min = {}

        for log_line in log_data:
            if self.logHelper.is_a_valid_prod_log_line(log_line):
                log_datetime = self.logHelper.get_time_from_prod_log_line(log_line)
                ip = self.logHelper.get_ip_from_prod_log_line(log_line)
                date_key = f"{log_datetime.year}/{log_datetime.month}/{log_datetime.day} {log_datetime.hour}:{log_datetime.minute:02d}"

                if date_key in date_ip_per_min:
                    if ip in date_ip_per_min[date_key]:
                        date_ip_per_min[date_key][ip]["req"] += 1
                    else:
                        date_ip_per_min[date_key][ip] = {"req": 1}
                else:
                    date_ip_per_min[date_key] = {ip: {"req": 1}}

        bad_ips = {
            date_key_v: {
                ip: {"req": count["req"]}
                for ip, count in ips.items()
                if count["req"] >= int(self.max_req_per_min)
            }
            for date_key_v, ips in date_ip_per_min.items()
        }

        no_bot_ips = self.__remove_good_bots(bad_ips)
        bad_ips = {date_key: ips for date_key, ips in no_bot_ips.items() if ips}

        return bad_ips

    # def __copy_prod_log(self):
    #     self.logHelper.transfer_prod_log_thru_scp()

    def generate_bot_report(self):
        total_lines = self.__get_total_lines_from_cache()

        last_index = (
            int(self.__get_last_processed_line_to_cache())
            if self.__get_last_processed_line_to_cache()
            else 0
        )

        numLineToStar = (
            (total_lines - last_index) if last_index < total_lines else total_lines
        )

        print(
            f"Total is {total_lines}  my last line was  {last_index} i will do tail {numLineToStar}"
        )

        logData = self.logHelper.retrieve_prod_log_from_this_line_number(numLineToStar)

        badip = self.__get_bad_ips_by_num_req_per_min(logData)
        self.logHelper.log_bad_ips(badip)
        self.__set_last_processed_line_to_cache(total_lines)
        print("finish ")

        # return [line for line in self.logHelper.read_prod_log()]
