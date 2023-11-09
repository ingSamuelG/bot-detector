import paramiko
import os
from sshConnector import sshConnector
import socket
import paramiko
import re
from datetime import datetime, timedelta


class logHelper:
    def __init__(self):
        self.ssh_server_con = sshConnector()
        self.prod_log_file_path = os.getenv("PROD_LOG_FILE_PATH")

    def get_time_from_prod_log_line(self, line):
        pattern = r"\[([\d/: ]+)\]"
        match = re.search(pattern, line)
        date_format = "%d/%m/%Y %H:%M:%S"
        if match:
            date_str = match.group(1)
            return datetime.strptime(date_str, date_format)
        else:
            raise ValueError("No match found for the given pattern.")

    def get_ip_from_prod_log_line(self, line):
        pattern = r"ip=([\d.]+)"
        match = re.search(pattern, line)
        if match:
            return match.group(1)
        else:
            raise ValueError("No match found for the given pattern.")

    def is_a_valid_prod_log_line(self, line):
        ip_pattern = r"ip=([\d.]+)"
        ip_match = re.search(ip_pattern, line)

        timeStamp_pattern = r"\[([\d/: ]+)\]"
        timeStamp_match = re.search(timeStamp_pattern, line)

        return ip_match and timeStamp_match

    def get_total_lines_for_prod_log(self):
        lines_in_bytes = self.ssh_server_con.exec_comand_in_server_get_stdout(
            f"wc -l {self.prod_log_file_path}"
        )
        lines = lines_in_bytes.decode("utf-8").split(" ")[0].strip()
        return lines

    def retrieve_prod_log_from_this_line_number(self, line):
        lines_in_bytes = self.ssh_server_con.exec_comand_in_server_get_stdout(
            f"tail -n {line} {self.prod_log_file_path}"
        )
        return lines_in_bytes.decode("utf-8").split("\n")

    def read_prod_log(self):
        with open(f".\\files\copy_prod.log", "r", encoding="utf-8") as file:
            for line in file:
                yield line.rstrip("\n")

    def transfer_prod_log_thru_scp(self):
        print(f"downloading files in the remote server {self.prod_log_file_path}")
        self.ssh_server_con.get_file_from_scp(self.prod_log_file_path, "copy_prod.log")
        print(f"file copied files in locally: copy_prod.log")

    def log_bad_ips(self, dic):
        with open(f".\\files\\test.log", "w") as log_file:
            for key, values in dic.items():
                # Write the key
                log_file.write(f"Key: {key}\n")
                # Iterate over the values in the list for this key
                for in_key, in_value in values.items():
                    # Write each value
                    log_file.write(f"\t{in_key}  num of request :{in_value}\n")

    def copy_log_from_server_ftp(self):
        pass
