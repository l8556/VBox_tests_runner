# -*- coding: utf-8 -*-
import time

from .commands import Commands as cmd
from subprocess import call, getoutput
from rich import print
from rich.console import Console
console = Console()

class VirtualMachine:
    def __init__(self, vm_name:str):
        self.name = vm_name

    def wait_boot(self):
        self._run_cmd(f"{cmd.wait} {self.name} VBoxServiceHeartbeat")

    def get_ip(self) -> str:
        print(f'{cmd.guestproperty} {self.name} "/VirtualBox/GuestInfo/Net/0/V4/IP"')
        with console.status("[red]Waiting for Net up") as status:
            while True:
                output = getoutput(f'{cmd.guestproperty} {self.name} "/VirtualBox/GuestInfo/Net/0/V4/IP"')
                status.update("[red]Waiting for Net up...")
                if output and output != 'No value set!':
                    return output.split(':')[1].strip()
                time.sleep(0.2)

    @staticmethod
    def _run_cmd(command):
        call(command, shell=True)

    def snapshot_list(self) -> list:
        return getoutput(f"{cmd.snapshot} {self.name} list").split('\n')

    def run(self, headless: bool = False) -> None:
        if self.check_status() is False:
            print(f"[green]|INFO| Starting VirtualMachine: {self.name}")
            return self._run_cmd(f'{cmd.startvm} {self.name}{" --type headless" if headless else ""}')
        print(f"[red]|INFO| VirtualMachine {self.name} already is running")

    def take_snapshot(self, name: str) -> None:
        self._run_cmd(f"{cmd.snapshot} {self.name} take {name}")

    def status(self):
        match self.check_status():
            case True:
                print(f"[green]|INFO| VirtualMachine {self.name} is running")
            case False:
                print(f"[red]|INFO| VirtualMachine {self.name} is poweroff")

    def check_status(self) -> bool:
        match self.get_parameter_info('VMState'):
            case "poweroff":
                return False
            case "running":
                return True
            case _:
                print(f"[red]|INFO| Unable to determine virtual machine {self.name} status")

    def get_parameter_info(self, parameter: str) -> str | None:
        for line in self.get_full_info().split('\n'):
            if line.lower().startswith(f"{parameter.lower()}="):
                return line.strip().split('=', 1)[1].strip().replace("\"", '')

    def get_full_info(self) -> str:
        return getoutput(f"{cmd.showvminfo} {self.name} --machinereadable")

    def restore_snapshot(self, name: str = None) -> None:
        print(f"[green]|INFO| Restoring snapshot to snapshot {name if name else self.snapshot_list()[-1].strip()}")
        self._run_cmd(f"{cmd.snapshot} {self.name} {f'restore {name}' if name else 'restorecurrent'}")

    def stop(self):
        print(f"[green]|INFO| Shutting down the virtual machine {self.name}")
        self._run_cmd(f'{cmd.controlvm} {self.name} poweroff')
        time.sleep(5)
