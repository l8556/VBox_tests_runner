# -*- coding: utf-8 -*-
import os.path
import time

from os.path import join

from frameworks.VBox import VirtualMachine
from frameworks.host_control import FileUtils
from frameworks.report import Report
from frameworks.ssh_client.ssh_client import SshClient
from rich.console import Console

from tests.data import LinuxData, HostData

console = Console()

class DesktopTests:
    def __init__(self, version: str):
        self.testing_hosts = FileUtils.read_json(join(os.getcwd(), 'config.json'))['hosts']
        self.version = version
        self.vm = None
        self.host = HostData()
        self.report_dir = join(self.host.report_dir, self.version)
        FileUtils.create_dir((self.report_dir, self.host.tmp_dir), silence=True)

    def run(self):
        for machine_name in self.testing_hosts:
            running_vm = self._run_vm(machine_name)
            self.vm = self._create_vm_data(running_vm, machine_name)
            self.run_script_on_vm()
            running_vm.stop()
        self._merge_reports()

    def _create_vm_data(self, running_vm, machine_name):
        return LinuxData(
            user=running_vm.get_logged_user(),
            version=self.version,
            ip=running_vm.get_ip(),
            name=machine_name
        )

    @staticmethod
    def _run_vm(machine_name) -> VirtualMachine:
        vm = VirtualMachine(machine_name)
        if vm.check_status():
            vm.stop()
        vm.restore_snapshot()
        vm.run(headless=True)
        vm.wait_net_up()
        return vm


    def _merge_reports(self):
        reports = FileUtils.get_paths(self.report_dir, name_include=f"{self.version}")
        Report().merge(reports,  join(self.report_dir, f"{self.version}_full_report.csv"))

    def run_script_on_vm(self):
        ssh = SshClient(self.vm.ip)
        ssh.connect(self.vm.user)
        self._create_vm_dirs(ssh)
        self._change_vm_service_dir_access(ssh)
        self._upload_files(ssh)
        self._start_my_service(ssh)
        self._wait_execute_script(ssh)
        ssh.ssh_exec(f'sudo systemctl disable {self.vm.my_service_name}')
        self._download_report(ssh)

    def _upload_files(self, ssh: SshClient):
        ssh.upload_file(self.host.tg_token, self.vm.tg_token_file)
        ssh.upload_file(self.host.tg_chat_id, self.vm.tg_chat_id_file)
        ssh.upload_file(self._create_file(join(self.host.tmp_dir, 'service'), self.vm.my_service()), self.vm.my_service_path)
        ssh.upload_file(self._create_file(join(self.host.tmp_dir, 'script.sh'),self.vm.script_sh()), self.vm.script_path)

    def _start_my_service(self, ssh: SshClient):
        ssh.ssh_exec_commands(self.vm.start_service_commands)

    def _create_vm_dirs(self, ssh: SshClient):
        ssh.ssh_exec(f'mkdir {self.vm.tg_dir}')

    def _change_vm_service_dir_access(self, ssh: SshClient):
        ssh.ssh_exec_commands([
            f'sudo chown {self.vm.user}:{self.vm.user} {self.vm.services_dir}',
            f'sudo chmod u+w {self.vm.services_dir}'
        ])

    def _wait_execute_script(self, ssh: SshClient):
        with console.status("[red]Waiting for execute script") as status:
            while ssh.exec_command(f'systemctl is-active {self.vm.my_service_name}') == 'active':
                status.update(ssh.exec_command(f'journalctl -n 20 -u {self.vm.my_service_name}'))
                time.sleep(0.1)
        console.print(ssh.exec_command(f'journalctl -b -1 -u {self.vm.my_service_name}'))

    def _download_report(self, ssh: SshClient):
        try:
            ssh.download_file(
                self.vm.report_path, join(self.report_dir,
                f'{self.version}_{self.vm.name}_desktop_report.csv')
            )
        except Exception as e:
            print(f"Exceptions when download report: {e}")

    @staticmethod
    def _create_file(path: str, text: str) -> str:
        FileUtils.file_writer(path, '\n'.join(line.strip() for line in text.split('\n')), newline='')
        return path
