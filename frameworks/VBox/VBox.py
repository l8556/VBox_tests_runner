from .commands import Commands as cmd
from subprocess import getoutput
from rich import print

class Vbox:
    @staticmethod
    def vm_list() -> list:
        return getoutput(cmd.list).split('\n')
    def check_vm_names(self, vm_names: list | str) -> list | str:
        vm_list = [vm.split()[0].replace('"', '') for vm in self.vm_list()]
        for name in [vm_names] if isinstance(vm_names, str) else vm_names:
            if name not in vm_list:
                raise print(f"[bold red]|ERROR| The Virtual Machine {name} not exists. Vm list:\n{vm_list}")
        return vm_names
