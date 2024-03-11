# -*- coding: utf-8 -*-
import os
from os.path import join, isdir

from host_tools import File
from invoke import task
from rich.prompt import Prompt
from rich import print
from telegram import Telegram

from frameworks.VBox import VirtualMachine, Vbox
from tests.data import TestData
from tests.desktop_tests import DesktopTests
import tests.multiprocessing as multiprocess
from frameworks.console import MyConsole
from tests.tools.desktop_report import DesktopReport

console = MyConsole().console
print = console.print


@task
def desktop_test(
        c,
        version=None,
        update_from=None,
        name=None,
        processes=None,
        detailed_telegram=False,
        custom_config=False,
        headless=False
):
    data = TestData(
        version=version if version else Prompt.ask('[red]Please enter version'),
        update_from=update_from,
        telegram=detailed_telegram,
        config_path=join(os.getcwd(), 'custom_config.json') if custom_config else join(os.getcwd(), 'config.json'),
        custom_config_mode=custom_config
    )

    num_processes = int(processes) if processes else 1
    report = DesktopReport(report_path=data.report_path)

    if num_processes > 1 and not name:
        return multiprocess.run(data.version, data.vm_names, num_processes, 10)
    else:
        for vm in Vbox().check_vm_names([name] if name else data.vm_names):
            DesktopTests(vm, data).run(headless=headless)

    report.get_full(data.version)
    report.send_to_tg(data.version, data.title, data.tg_token, data.tg_chat_id, data.update_from) if not name else ...


@task
def run_vm(c, name: str = '', headless=False):
    vm = VirtualMachine(Vbox().check_vm_names(name))
    vm.run(headless=headless)
    vm.wait_net_up(status_bar=True)
    vm.wait_logged_user(status_bar=True)
    return print(f"[green]ip: [red]{vm.get_ip()}[/]\nuser: [red]{vm.get_logged_user()}[/]")


@task
def stop_vm(c, name: str = None, group_name: str = None):
    if name:
        VirtualMachine(Vbox().check_vm_names(name)).stop()
    else:
        Prompt.ask(f"[red]|WARNING| All running virtual machines will be stopped. Press Enter to continue.")
        vms_list = Vbox().vm_list(group_name=group_name)
        for vm_info in vms_list:
            virtualmachine = VirtualMachine(vm_info[1])
            if virtualmachine.check_status():
                print(f"[green]|INFO| Shutting down the virtual machine: [red]{vm_info[0]}[/]")
                virtualmachine.stop()


@task
def vm_list(c, group_name: str = None):
    print(Vbox().vm_list(group_name))


@task
def out_info(c, name: str = ''):
    print(VirtualMachine(Vbox().check_vm_names(name)).get_info())
