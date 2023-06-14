# -*- coding: utf-8 -*-
from invoke import task
from rich.prompt import Prompt
from rich import print

from frameworks.VBox import VirtualMachine, Vbox
from tests.desktop_tests import DesktopTests

@task
def desktop_test(c, version=None):
    version = version if version else Prompt.ask('[red]Please enter version')
    DesktopTests(version=version).run()

@task
def run_vm(c, name: str = '', headless=False):
    if name in [vm.split()[0].replace('"', '') for vm in Vbox.vm_list()]:
        vm = VirtualMachine(name)
        vm.run(headless=headless)
        vm.wait_net_up()
        return print(vm.get_ip()), print(vm.get_logged_user())
    print(f"[bold red]|ERROR| The Virtual Machine {name} not exists. Vm list:\n{Vbox.vm_list()}")

@task
def stop_vm(c, name: str = ''):
    VirtualMachine(name).stop()

@task
def vm_list(c):
    print(Vbox.vm_list())
