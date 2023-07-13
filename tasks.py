# -*- coding: utf-8 -*-
import json
import os
from os.path import join, isfile

from invoke import task
from rich.prompt import Prompt
from rich import print
from frameworks.VBox import VirtualMachine, Vbox
from frameworks.host_control import FileUtils
from frameworks.telegram import Telegram
from tests.data import HostData
from tests.desktop_tests import DesktopTests
import tests.multiprocessing as multiprocess
from frameworks.console import MyConsole
from tests.tools.desktop_report import DesktopReport

console = MyConsole().console
print = console.print


@task
def desktop_test(c, version=None, name=None, processes=None, detailed_telegram=False, custom_config=False):
    version = version if version else Prompt.ask('[red]Please enter version')
    config = join(os.getcwd(), 'custom_config.json') if custom_config else join(os.getcwd(), 'config.json')
    vm_names = [name] if name else FileUtils.read_json(config)['hosts']
    num_processes = int(processes) if processes else 1
    msg = f"{FileUtils.read_json(config).get('title')} desktop editors tests completed on version: {version}"
    if num_processes > 1:
        multiprocess.run(version, Vbox().check_vm_names(vm_names), num_processes, 10)
        Telegram().send_document(
            DesktopReport(version=version, report_dir=join(HostData(config).report_dir)).merge_reports(),
            caption=msg
        )
    else:
        for vm in Vbox().check_vm_names(vm_names):
            DesktopTests(
                version=version,
                vm_name=vm,
                telegram=detailed_telegram,
                config_path=config,
                custom_config=custom_config
            ).run()
    full_report = DesktopReport(version=version, report_dir=join(HostData(config).report_dir)).merge_reports()
    if not name:
        Telegram().send_document(full_report, caption=msg)

@task
def run_vm(c, name: str = '', headless=False):
    vm = VirtualMachine(Vbox().check_vm_names(name))
    vm.run(headless=headless)
    vm.wait_net_up(status_bar=True)
    return print(vm.get_ip()), print(vm.wait_logged_user())

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
