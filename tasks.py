# -*- coding: utf-8 -*-
import os
from os.path import join

from invoke import task
from rich.prompt import Prompt
from rich import print
from frameworks.VBox import VirtualMachine, Vbox
from tests.data import TestData
from tests.desktop_tests import DesktopTests
import tests.multiprocessing as multiprocess
from frameworks.console import MyConsole
from tests.tools.desktop_report import DesktopReport

console = MyConsole().console
print = console.print


@task
def desktop_test(c, version=None, name=None, processes=None, detailed_telegram=False, custom_config=False, headless=False):
    data = TestData(
        version=version if version else Prompt.ask('[red]Please enter version'),
        telegram=detailed_telegram,
        config_path=join(os.getcwd(), 'custom_config.json') if custom_config else join(os.getcwd(), 'config.json'),
        custom_config_mode=custom_config
    )

    num_processes = int(processes) if processes else 1
    report = DesktopReport(report_path=data.full_report_path)

    if num_processes > 1 and not name:
        return multiprocess.run(data.version, data.vm_names, num_processes, 10)
    else:
        for vm in Vbox().check_vm_names([name] if name else data.vm_names):
            DesktopTests(vm, data).run(headless=False if headless else True)

    report.get_full(data.version)
    report.send_to_tg(data.version, data.title, data.tg_token, data.tg_chat_id) if not name else ...


@task
def run_vm(c, name: str = '', headless=False):
    vm = VirtualMachine(Vbox().check_vm_names(name))
    vm.run(headless=headless)
    vm.wait_net_up(status_bar=True)
    vm.wait_logged_user(status_bar=True)
    return print(vm.get_ip()), print(vm.get_logged_user())


@task
def stop_vm(c, name: str = '', all: bool = False):
    if all:
        for vm in [line.split('"')[1] for line in Vbox.vm_list()]:
            return VirtualMachine(vm).stop()
    VirtualMachine(Vbox().check_vm_names(name)).stop()


@task
def vm_list(c):
    print(Vbox.vm_list())


@task
def out_info(c, name: str = ''):
    print(VirtualMachine(Vbox().check_vm_names(name)).get_info())
