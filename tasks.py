# -*- coding: utf-8 -*-
import os
from os.path import join

from invoke import task
from rich.prompt import Prompt
from rich import print
from frameworks.VBox import VirtualMachine, Vbox
from frameworks.host_control import FileUtils
from frameworks.telegram import Telegram
from tests.data import TestData
from tests.desktop_tests import DesktopTests
import tests.multiprocessing as multiprocess
from frameworks.console import MyConsole
from tests.tools.desktop_report import DesktopReport

console = MyConsole().console
print = console.print

@task
def desktop_test(c, version=None, name=None, processes=None, detailed_telegram=False, custom_config=False):
    config_path = join(os.getcwd(), 'custom_config.json') if custom_config else join(os.getcwd(), 'config.json')
    test_data = TestData(
        version=version if version else Prompt.ask('[red]Please enter version'),
        telegram=detailed_telegram,
        config_path=config_path,
        custom_config_mode=custom_config
    )
    num_processes = int(processes) if processes else 1
    report = DesktopReport(version=test_data.version, report_dir=test_data.report_dir)
    if num_processes > 1 and not name:
        multiprocess.run(test_data.version, test_data.vm_names, num_processes, 10)
        test_data.tg.send_document(report.get_full(test_data.title, caption=test_data.complete_test_msg))
    else:
        for vm in Vbox().check_vm_names([name] if name else test_data.vm_names):
            DesktopTests(vm, test_data).run()
    full_report = report.get_full(test_data.title)
    test_data.tg.send_document(full_report, caption=test_data.complete_test_msg) if not name else ...

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
        for vm in Vbox.vm_list():
            VirtualMachine(vm).stop()
        return
    VirtualMachine(Vbox().check_vm_names(name)).stop()

@task
def vm_list(c):
    print(Vbox.vm_list())

@task
def out_info(c, name: str = ''):
    VirtualMachine(Vbox().check_vm_names(name)).out_info()
