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

    def __del__(self):
        self.close_ssh_chanel()
        self.close()

    def upload_file(self, local, remote):
        sftp = self.client.open_sftp()
        sftp.put( local, remote)


    def connect(self, username: str):
        try:
            self.load_keys()
            self.client.connect(self.host, username=username)
        except Exception as e:
            print(f"[red]|ERROR| Failed to connect: {username}@{self.host}. Exception: {e}")

    def exec_command(self, command: str) -> str | None:
        channel = self.client.get_transport().open_session()
        channel.exec_command(command)
        channel.recv_exit_status()
        output = channel.recv(4096).decode()
        print('Output:')
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
            while not  self.ssh.recv_ready():
            # Добавляем задержку, чтобы не перегружать процессор
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
            # Проверяем, есть ли данные для чтения
            if self.ssh.recv_ready():
                output += self.ssh.recv(1024).decode()
                command_output = '\n'.join(output.split('\n')[1:-1])  # Исключаем первую и последнюю строку
                print(command_output)
            else:
                # Если данных больше нет, выходим из цикла чтения
                break
        # output = ''
        # while self.ssh.recv_ready():
        #     output += self.ssh.recv(10000).decode()
        # command_output = '\n'.join(output.split('\n')[1:-1])  # Исключаем первую и последнюю строку
        # print(command_output)
        # return command_output


    def test(self):
        command = 'apt update'
        stdin, stdout, stderr = self.client.exec_command(command)
        # Ожидание завершения выполнения команды
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print('Команда выполнена успешно')
        else:
            print(f'Команда выполнена с ошибкой. Статус: {exit_status}')

if __name__ == "__main__":
    kubuntu = SshClient('192.168.0.114')
    kubuntu.connect('l02')
    # command = f'cd /home/l02/scripts/oo_desktop_testing; poetry shell; inv desktop;'
    # kubuntu.test()
    # думаю стоит сделать запуск через сервис с проверкой статуса сервиса пока сервис запушен ожидать и выводить лог

    # kubuntu.exec_command(command)
    # kubuntu.ssh_exec('cd ./scripts/oo_desktop_testing')
    # kubuntu.read_output()
    # kubuntu.ssh_exec('exec_command')
    # time.sleep(2)
    # # kubuntu.wait_command()
    # kubuntu.read_output()
    # kubuntu.ssh_exec('inv desktop')
    # kubuntu.read_output()
    # kubuntu.ssh_exec('ll')
    # time.sleep(0.2)
    # kubuntu.read_output()
    # kubuntu.close()