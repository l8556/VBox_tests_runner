# -*- coding: utf-8 -*-
import os
import time
from os.path import basename

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
        self.close_sftp_chanel()
        self.close_ssh_chanel()
        self.close()

    def close_sftp_chanel(self):
        if self.sftp:
            self.sftp.close()

    def upload_file(self, local, remote):
        if self.sftp:
            print(f'[green]|INFO| Upload file: {basename(local)} to {remote}')
            self.sftp.putfo(open(local, 'rb'), remote)
            local_file_size = os.stat(local).st_size
            while True:
                remote_file_size = self.sftp.stat(remote).st_size
                if remote_file_size == local_file_size:
                    break
        else:
            print(f'[red]|WARNING| Sftp chanel not created.')

    def download_file(self, remote, local):
        if self.sftp:
            with open(local, 'wb') as local_file:
                transfer = self.sftp.getfo(remote, local_file)
                remote_file_size = self.sftp.stat(remote).st_size
                while local_file.tell() < remote_file_size:
                    time.sleep(0.2)
        else:
            print(f'[red]|WARNING| Sftp chanel not created.')

    def create_sftp_chanel(self):
        self.sftp = self.client.open_sftp()

    def connect(self, username: str, timeout: int = 300):
        print(f"[green]|INFO| Connect to host: {self.host}")
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                self.load_keys()
                self.client.connect(self.host, username=username)
                self.create_ssh_chanel()
                self.create_sftp_chanel()
                print('[green]|INFO|Connected')
                break

            except paramiko.AuthenticationException:
                print('Authentication failed. Waiting and retrying...')
                time.sleep(3)
                continue
            except paramiko.SSHException as e:
                print(f'SSH error: {e}. Waiting and retrying...')
                time.sleep(3)
                continue
            except Exception as e:
                print(f"[red]|ERROR| Failed to connect: {username}@{self.host}.\nWaiting and retrying...")
                time.sleep(3)
                continue

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
            time.sleep(1)
            while not self.ssh.recv_ready():
                time.sleep(0.5)
            return
        print(f"[red]|WARNING| SSH Chanel not created")

    def ssh_exec_commands(self, commands: list):
        for command in commands:
            ssh_channel = self.client.get_transport().open_session()
            print(f"[green]|INFO| Exec command: {command}")
            ssh_channel.exec_command(command)
            while True:
                if ssh_channel.recv_ready():
                     print(ssh_channel.recv(4096).decode('utf-8'))
                if ssh_channel.exit_status_ready():
                    break

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
