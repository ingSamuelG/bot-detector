import paramiko
import os
from scp import SCPClient


class sshConnector:
    def __init__(self):
        self.ssh = paramiko.SSHClient()
        REMOTE_SERVER_IP = os.getenv("REMOTE_SERVER_IP")
        REMOTE_PASS = os.getenv("REMOTE_PASS")
        REMOTE_USER = os.getenv("REMOTE_USER")

        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(
            hostname=REMOTE_SERVER_IP,
            username=REMOTE_USER,
            password=REMOTE_PASS,
        )

        # self.sftp = self.ssh.open_sftp()
        self.scp = SCPClient(self.ssh.get_transport())

    def get_file_from_scp(self, remote_file_path, new_file_name):
        self.scp.get(remote_file_path, f".\\files\{new_file_name}")

    def exec_comand_in_server_get_stdout(self, cmd):
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        lines_in_bytes = stdout.read()
        return lines_in_bytes

    def close_conn(self):
        self.scp.close()
        self.ssh.close()
