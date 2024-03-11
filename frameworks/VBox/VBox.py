from . import VirtualMachine
from .commands import Commands as cmd
from subprocess import getoutput
from rich import print

class Vbox:
    @staticmethod
    def vm_list(group_name: str = None) -> list[list[str]]:
        vm_list = [
            [vm[0].replace('"', ''), vm[1].translate(str.maketrans('', '', '{}'))]
            for vm in [vm.split() for vm in getoutput(cmd.list).split('\n')]
        ]
        if isinstance(group_name, str):
            return [vm for vm in vm_list if VirtualMachine(vm[1]).get_group_name() == group_name]
        return vm_list

    def check_vm_names(self, vm_names: list | str) -> list | str:
        existing_names = self.get_vm_names()
        for name in [vm_names] if isinstance(vm_names, str) else vm_names:
            if name not in existing_names:
                raise print(f"[bold red]|ERROR| The Virtual Machine {name} not exists. Vm list:\n{existing_names}")
        return vm_names

    def get_vm_names(self, group_name: str = None) -> list:
        return [vm[0] for vm in self.vm_list(group_name)]

    def get_vm_uuids(self, group_name: str = None) -> list:
        return [vm[1] for vm in self.vm_list(group_name)]
