# -*- coding: utf-8 -*-
import os
from os.path import join

from invoke import task
from rich.prompt import Prompt
from rich import print

from frameworks.VBox import VirtualMachine, Vbox
from frameworks.host_control import FileUtils
from tests.desktop_tests import DesktopTests


@task
def desktop_test(c, version=None, name=None, processes=None):
    version = version if version else Prompt.ask('[red]Please enter version')
    vm_names = [name] if name else FileUtils.read_json(join(os.getcwd(), 'config.json'))['hosts']
    num_processes = int(processes) if processes else 1
    if num_processes > 1:
        return DesktopTests(version=version).run_multiprocessing(Vbox().check_vm_names(vm_names), num_processes)
    DesktopTests(version=version).run_single_process(Vbox().check_vm_names(vm_names))

@task
def run_vm(c, name: str = '', headless=False):
    vm = VirtualMachine(Vbox().check_vm_names(name))
    vm.run(headless=headless)
    vm.wait_net_up()
    return print(vm.get_ip()), print(vm.get_logged_user())

@task
def stop_vm(c, name: str = ''):
    VirtualMachine(Vbox().check_vm_names(name)).stop()

@task
def vm_list(c):
    print(Vbox.vm_list())

@task
def out_info(c, name: str = ''):
    VirtualMachine(Vbox().check_vm_names(name)).out_info()
