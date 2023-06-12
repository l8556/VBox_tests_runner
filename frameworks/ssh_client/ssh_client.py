# -*- coding: utf-8 -*-
import time

import paramiko
from paramiko.client import SSHClient
from rich import print


class SshClient:
    def __init__(self, host: str):
        self.host = host
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh = None
        self.sftp = None

    def __del__(self):
        self.close_ssh_chanel()
        self.close()

    def upload_file(self, local, remote):
        sftp = self.client.open_sftp()
        sftp.put(local, remote)

    def connect(self, username: str):
        try:
            self.load_keys()
            self.client.connect(self.host, username=username)
        except Exception as e:
            print(f"[red]|ERROR| Failed to connect: {username}@{self.host}. Exception: {e}")

    def exec_command(self, command: str) -> str | None:
        stdin, stdout, stderr = self.client.exec_command(command)
        output = stdout.read().decode('utf-8').strip()
        print(output)
        return output

    def load_keys(self):
        try:
            self.client.load_system_host_keys()
        except Exception as e:
            print(e)

    def close(self):
        self.client.close()

    def create_ssh_chanel(self):
        self.ssh = self.client.invoke_shell()

    def close_ssh_chanel(self):
        if self.ssh is not None:
            self.ssh.close()

    def ssh_exec(self, command):
        if self.ssh is not None:
            print(f"[green]|INFO| Exec command: {command}")
            self.ssh.send(f'{command}\n')
            time.sleep(0.5)
            while not  self.ssh.recv_ready():
                time.sleep(0.1)
            return
        print(f"[red]|WARNING| SSH Chanel not created")

    def wait_command(self):
        while not self.ssh.exit_status_ready():
            print(self.ssh.exit_status_ready())
            time.sleep(0.1)
            continue

    def read_output(self):
        while not self.ssh.recv_ready():
            time.sleep(0.1)
            continue
        output = ''
        while True:
            if self.ssh.recv_ready():
                output += self.ssh.recv(1024).decode()
                command_output = '\n'.join(output.split('\n')[1:-1])
                print(command_output)
            else:
                break

    def test(self):
        command = 'apt update'
        stdin, stdout, stderr = self.client.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print('Success')
        else:
            print(f'Error: {exit_status}')
