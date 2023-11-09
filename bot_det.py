from logHelper import logHelper
import redis
import os
import socket
import paramiko
import re
from datetime import datetime, timedelta


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
                self.cache.setex("total_lines", 10800, total)
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

    def __get_bad_ips_by_num_req_per_min(self, log_data):
        bad_ips = []
        ip_per_min = {}
        date_ip_per_min = {}
        current_minutes = 1
        endTime = self.logHelper.get_time_from_prod_log_line(log_data[0]) + timedelta(
            minutes=1
        )

        for log_line in log_data:
            if self.logHelper.is_a_valid_prod_log_line(log_line):
                log_datetime = self.logHelper.get_time_from_prod_log_line(log_line)
                ip = self.logHelper.get_ip_from_prod_log_line(log_line)
                date_key = f"{log_datetime.year}/{log_datetime.month}/{log_datetime.day} {log_datetime.hour}:{log_datetime.minute:02d}"

                if date_key in date_ip_per_min:
                    if ip in date_ip_per_min[date_key]:
                        date_ip_per_min[date_key][ip] += 1
                    else:
                        date_ip_per_min[date_key][ip] = 1
                else:
                    date_ip_per_min[date_key] = {ip: 1}

        bad_ips = {
            date_key_v: {
                ip: count for ip, count in ips.items() if count >= self.max_req_per_min
            }
            for date_key_v, ips in date_ip_per_min.items()
        }

        # Remove date_key if it has no IPs meeting the threshold
        bad_ips = {date_key: ips for date_key, ips in bad_ips.items() if ips}

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

        logData = self.logHelper.retrieve_prod_log_from_this_line_number(numLineToStar)

        self.__get_bad_ips_by_num_req_per_min(logData[1:1000])
        return logData[0]

        # return [line for line in self.logHelper.read_prod_log()]
