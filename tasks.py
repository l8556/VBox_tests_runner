# -*- coding: utf-8 -*-
import os
from os.path import join, isfile

from invoke import task
from rich.prompt import Prompt
from rich import print
from frameworks.VBox import VirtualMachine, Vbox
from frameworks.host_control import FileUtils
from frameworks.telegram import Telegram
from tests.desktop_tests import DesktopTests
import tests.multiprocessing as multiprocess
from frameworks.console import MyConsole
console = MyConsole().console
print = console.print


@task
def desktop_test(c, version=None, name=None, processes=None, detailed_telegram=False, custom_config=False, full=False):
    version = version if version else Prompt.ask('[red]Please enter version')
    vm_names = [name] if name else _get_hosts(custom_config)
    num_processes = int(processes) if processes else 1
    msg = f"Full testing of Desktop Editors Completed on version: {version}"
    if num_processes > 1:
        multiprocess.run(version, Vbox().check_vm_names(vm_names), num_processes, 10)
        Telegram().send_document(DesktopTests(version=version, vm_name='None').merge_reports(), caption=msg)
    else:
        for vm in Vbox().check_vm_names(vm_names):
            DesktopTests(
                version=version,
                vm_name=vm,
                status=console.status(''),
                telegram=detailed_telegram,
                custom_config=True if custom_config or full else False
            ).run()
    full_report = DesktopTests(version=version, vm_name='None').merge_reports()
    if not name:
        Telegram().send_document(full_report, caption=msg)

def _get_hosts(custom_config: bool = False, full: bool =False) -> list:
    config_path = join(os.getcwd(), 'config.json')
    custom_config_path = join(os.getcwd(), 'custom_coinfigs', 'portal_config.json')
    if (custom_config and isfile(custom_config_path)) or (full and isfile(custom_config_path)):
        if full:
            return FileUtils.read_json(config_path)['hosts'] + FileUtils.read_json(custom_config_path)['hosts']
        return FileUtils.read_json(custom_config_path)['hosts']
    return FileUtils.read_json(config_path)['hosts']

@task
def run_vm(c, name: str = '', headless=False):
    vm = VirtualMachine(Vbox().check_vm_names(name))
    vm.run(headless=headless)
    vm.wait_net_up(status=console.status(''))
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


def _run_test(version):
    test = DesktopTests(version=version)
    test.desktop_test()