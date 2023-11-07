import paramiko
import os


class logHelper:
    def __init__(self):
        self.ssh = paramiko.SSHClient()

    def get_total_lines(self):
        REMOTE_SERVER_IP = os.getenv("REMOTE_SERVER_IP")
        REMOTE_PASS = os.getenv("REMOTE_PASS")
        REMOTE_USER = os.getenv("REMOTE_USER")

        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(
            hostname=REMOTE_SERVER_IP,
            username=REMOTE_USER,
            password=REMOTE_PASS,
        )
        stdin, stdout, stderr = self.ssh.exec_command(
            "wc -l /var/www/fx3.1/logs/production.log"
        )
        lines = stdout.read()
        self.ssh.close()
        return lines.decode("utf-8")
