# -*- coding: utf-8 -*-
import os
import time
from os.path import basename, join, exists
import paramiko
from paramiko.client import SSHClient
from frameworks.console import MyConsole

console = MyConsole().console
print = console.print

class SshClientException(Exception): ...

class SshClient:
    def __init__(self, ip: str, name: str = None):
        self.host_name = name if name else ''
        self.host = ip
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh = None
        self.sftp = None

    def __del__(self):
        self.close_sftp_chanel()
        self.close_ssh_chanel()
        self.close()

    def connect(self, username: str, timeout: int = 300):
        print(f"[green]|INFO|{self.host_name}|{self.host}| Connect to host.")
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                self.load_keys()
                self.client.connect(self.host, username=username)
                self.create_ssh_chanel()
                self.create_sftp_chanel()
                print(f'[green]|INFO|{self.host_name}|{self.host}| Connected.')
                break

            except paramiko.AuthenticationException:
                print(f'[red]|ERROR|{self.host_name}|{self.host}| Authentication failed. Waiting and retrying...')
                time.sleep(1)
                continue
            except paramiko.SSHException as e:
                print(f'[red]|ERROR|{self.host_name}|{self.host}| SSH error: {e}. Waiting and retrying...')
                time.sleep(1)
                continue
            except ConnectionError as e:
                print(
                    f"[red]|ERROR|{self.host_name}|{self.host}| {e} "
                    f"Failed to connect: {username}.\nWaiting and retrying..."
                )
                time.sleep(1)
                continue

    def close_sftp_chanel(self):
        if self.sftp:
            self.sftp.close()

    def upload_file(self, local: str, remote: str):
        if self.sftp:
            if exists(local):
                print(f'[green]|INFO|{self.host_name}|{self.host}| Upload file: {basename(local)} to {remote}')
                self.sftp.putfo(open(local, 'rb'), remote)
                local_file_size = os.stat(local).st_size
                while True:
                    remote_file_size = self.sftp.stat(remote).st_size
                    if remote_file_size == local_file_size:
                        break
            else:
                print(f"[cyan]|INFO|{self.host_name}| Local file not exists: {local}")
        else:
            raise SshClientException(f'[red]|WARNING|{self.host_name}|{self.host}| Sftp chanel not created.')

    def download_dir(self, remote: str, local: str):
        if self.sftp:
            for entry in self.sftp.listdir_attr(remote):
                remote_filename = join(remote, entry.filename).replace('\\', '/')
                local_filename = join(local, entry.filename)
                if entry.st_mode & 0o170000 == 0o040000:
                    os.makedirs(local_filename, exist_ok=True)
                    self.download_dir(remote_filename, local_filename)
                else:
                    self.download_file(remote_filename, local_filename)

    def download_file(self, remote: str, local: str):
        if self.sftp:
            with open(local, 'wb') as local_file:
                self.sftp.getfo(remote, local_file)
                remote_file_size = self.sftp.stat(remote).st_size
                while local_file.tell() < remote_file_size:
                    time.sleep(0.2)
        else:
            raise SshClientException(f'[red]|WARNING|{self.host_name}|{self.host}| Sftp chanel not created.')

    def create_sftp_chanel(self):
        self.sftp = self.client.open_sftp()

    def wait_execute_service(self, service_name: str, timeout: int = None, status_bar: bool = False):
        start_time = time.time()
        msg = f"[cyan]|INFO|{self.host_name}|{self.host}| Waiting for execute {service_name}"
        status = console.status(msg)
        status.start() if status_bar else print(msg)
        while self.get_service_status(service_name):
            status.update(f"{msg}\n{self.get_service_log(service_name)}") if status_bar else ...
            time.sleep(0.5)
            if isinstance(timeout, int) and (time.time() - start_time) >= timeout:
                status.stop() if status_bar else ...
                raise SshClientException(
                    f'[bold red]|WARNING|{self.host_name}|{self.host}| '
                    f'The service {service_name} waiting time has expired.'
                )
        status.stop() if status_bar else ...
        print(
            f"[blue]{'-' * 90}\n|INFO|{self.host_name}|{self.host}|Service {service_name} log:\n{'-' * 90}\n\n"
            f"{self.get_service_log(service_name, 1000)}\n{'-' * 90}"
        )

    def get_service_log(self, service_name: str, line_num: str | int = 20) -> str:
        return self.exec_command(f'sudo journalctl -n {line_num} -u {service_name}')

    def get_service_status(self, service_name: str) -> bool:
        return self.exec_command(f'systemctl is-active {service_name}') == 'active'

    def exec_command(self, command: str) -> str | None:
        stdin, stdout, stderr = self.client.exec_command(command)
        return stdout.read().decode('utf-8').strip()

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

    def ssh_exec(self, command: str):
        if self.ssh is not None:
            print(f"[green]|INFO|{self.host_name}|{self.host}| Exec command: {command}")
            self.ssh.send(f'{command}\n')
            time.sleep(1)
            while not self.ssh.recv_ready():
                time.sleep(0.5)
            return
        print(f"[red]|WARNING|{self.host_name}|{self.host}| SSH Chanel not created")

    def ssh_exec_commands(self, commands: list | str):
        for command in commands if isinstance(commands, list) else [commands]:
            ssh_channel = self.client.get_transport().open_session()
            print(f"[green]|INFO|{self.host_name}|{self.host}| Exec command: {command}")
            ssh_channel.exec_command(command)
            while True:
                time.sleep(0.5)
                if ssh_channel.recv_ready():
                    print(ssh_channel.recv(4096).decode('utf-8'))
                if ssh_channel.exit_status_ready():
                    break
