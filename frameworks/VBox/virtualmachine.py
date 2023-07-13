# -*- coding: utf-8 -*-
import time

from .commands import Commands as cmd
from subprocess import call, getoutput
from ..console import MyConsole

console = MyConsole().console
print = console.print

class VirtualMachinException(Exception): ...

class VirtualMachine:
    def __init__(self, vm_name:str):
        self.name = vm_name

    def audio(self, turn: bool):
        self._run_cmd(f"{cmd.modifyvm} {self.name} --audio-driver {'default' if turn else 'none'}")
        print(f"[green]|INFO|{self.name}| Audio interface is {'on' if turn else 'off'}")

    def set_cpus(self, num: int):
        self._run_cmd(f"{cmd.modifyvm} {self.name} --cpus {num}")
        print(f"[green]|INFO|{self.name}| The number of processor cores is set to {num}")

    def set_memory(self, num: int):
        self._run_cmd(f"{cmd.modifyvm} {self.name} --memory {num}")
        print(f"[green]|INFO|{self.name}| Installed RAM quantity: {num}")

    def wait_logged_user(self, timeout: int = 300, status_bar: bool = True) -> None:
        start_time = time.time()
        status_msg = f"[cyan]|INFO|{self.name}| Waiting for Logged In Users List"
        status = console.status(status_msg)
        status.start() if status_bar else print(status_msg)
        while time.time() - start_time < timeout:
            status.update(f"{status_msg}: {(time.time() - start_time):.00f}/{timeout}") if status_bar else ...
            user_name = self.get_logged_user()
            if user_name:
                status.stop() if status_bar else ...
                print(f'[green]|INFO|{self.name}| List of logged-in user {user_name}')
                break
            time.sleep(1)
        else:
            raise VirtualMachinException(
                f"[red]|ERROR|{self.name}| Waiting time for the virtual machine {self.name} "
                f"Logged In Users List has expired"
            )

    def get_logged_user(self) -> str | None:
        output = getoutput(f'{cmd.guestproperty} {self.name} "/VirtualBox/GuestInfo/OS/LoggedInUsersList"')
        if output and output != 'No value set!':
            if len(output.split(':')) >= 2:
                return output.split(':')[1].strip()
        return None

    def wait_net_up(self, timeout: int = 300, status_bar: bool = True):
        start_time = time.time()
        msg = f"[cyan]|INFO|{self.name}| Waiting for network adapter up"
        status = console.status(msg)
        status.start() if status_bar else print(msg)
        while time.time() - start_time < timeout:
            status.update(f"{msg}: {(time.time() - start_time):.00f}/{timeout}") if status_bar else ...
            ip_address = self.get_ip()
            if ip_address:
                status.stop() if status_bar else ...
                print(f'[green]|INFO|{self.name}| The network adapter is running, ip: {ip_address}')
                break
            time.sleep(1)
        else:
            raise VirtualMachinException(
                f"[red]|ERROR|{self.name}| Waiting time for the virtual machine network adapter to start has expired"
            )

    def get_ip(self) -> str | None:
        output = getoutput(f'{cmd.guestproperty} {self.name} "/VirtualBox/GuestInfo/Net/0/V4/IP"')
        if output and output != 'No value set!':
            return output.split(':')[1].strip()
        return None

    def snapshot_list(self) -> list:
        return getoutput(f"{cmd.snapshot} {self.name} list").split('\n')

    def run(self, headless: bool = False) -> None:
        if self.check_status() is False:
            print(f"[green]|INFO|{self.name}| Starting VirtualMachine")
            return self._run_cmd(f'{cmd.startvm} {self.name}{" --type headless" if headless else ""}')
        print(f"[red]|INFO|{self.name}| VirtualMachine already is running")

    def take_snapshot(self, name: str) -> None:
        self._run_cmd(f"{cmd.snapshot} {self.name} take {name}")

    def status(self):
        match self.check_status():
            case True:
                print(f"[green]|INFO|{self.name}| VirtualMachine is running")
            case False:
                print(f"[red]|INFO|{self.name}| VirtualMachine is poweroff")

    def check_status(self) -> bool:
        match self.get_parameter_info('VMState'):
            case "poweroff":
                return False
            case "running":
                return True
            case _:
                print(f"[red]|INFO|{self.name}| Unable to determine virtual machine status")

    def get_parameter_info(self, parameter: str) -> str | None:
        for line in self.get_full_info().split('\n'):
            if line.lower().startswith(f"{parameter.lower()}="):
                return line.strip().split('=', 1)[1].strip().replace("\"", '')

    def get_full_info(self) -> str:
        return getoutput(f"{cmd.showvminfo} {self.name} --machinereadable")

    def restore_snapshot(self, name: str = None) -> None:
        print(f"[green]|INFO|{self.name}| Restoring snapshot: {name if name else self.snapshot_list()[-1].strip()}")
        self._run_cmd(f"{cmd.snapshot} {self.name} {f'restore {name}' if name else 'restorecurrent'}")

    def stop(self):
        print(f"[green]|INFO|{self.name}| Shutting down the virtual machine")
        self._run_cmd(f'{cmd.controlvm} {self.name} poweroff')
        time.sleep(5)

    def out_info(self):
        self._run_cmd(f'{cmd.enumerate} {self.name}')

    @staticmethod
    def _run_cmd(command):
        call(command, shell=True)
