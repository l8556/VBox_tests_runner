# -*- coding: utf-8 -*-
from os.path import join

from frameworks.VBox import VirtualMachine
from frameworks.console import MyConsole
from frameworks.host_control import FileUtils
from frameworks.report import Report
from frameworks.ssh_client.ssh_client import SshClient
from frameworks.telegram import Telegram
from tests.data import LinuxData, HostData

console = MyConsole().console
print = console.print


class DesktopTests:
    def __init__(self, version: str):
        self.host = HostData()
        self.tg = Telegram(token_path=self.host.tg_token, chat_id_path=self.host.tg_chat_id, tmp_dir=self.host.tmp_dir)
        self.test_status = None
        self.version = version
        self.vm = None
        self.report_dir = join(self.host.report_dir, self.version)
        FileUtils.create_dir((self.report_dir, self.host.tmp_dir), silence=True)

    def run(self, machine_names: str | list, tg_msg: str = None):
        self.test_status = console.status('')
        for name in machine_names if isinstance(machine_names, list) else [machine_names]:
            self.desktop_test(name)
        if tg_msg:
            self.tg.send_document(self.merge_reports(), caption=tg_msg)

    def desktop_test(self, vm_name: str):
        vm = VirtualMachine(vm_name)
        self.vm = self._create_data_vm(self._run_vm(vm), vm_name)
        self.run_script_on_vm()
        vm.stop()

    def _create_data_vm(self, running_vm, machine_name):
        return LinuxData(
            user=running_vm.get_logged_user(status=self.test_status),
            version=self.version,
            ip=running_vm.get_ip(),
            name=machine_name
        )

    def _run_vm(self, vm: VirtualMachine) -> VirtualMachine:
        if vm.check_status():
            vm.stop()
        vm.restore_snapshot()
        vm.run(headless=True)
        vm.wait_net_up(status=self.test_status)
        return vm

    def merge_reports(self):
        full_report = join(self.report_dir, f"{self.version}_full_report.csv")
        reports = FileUtils.get_paths(self.report_dir, name_include=f"{self.version}", extension='csv')
        Report().merge(reports, full_report)
        return full_report

    def run_script_on_vm(self):
        ssh = SshClient(self.vm.ip, self.vm.name)
        ssh.connect(self.vm.user)
        self._create_vm_dirs(ssh)
        self._change_vm_service_dir_access(ssh)
        self._upload_files(ssh)
        self._start_my_service(ssh)
        self._wait_execute_service(ssh)
        self._download_report(ssh)

    def _upload_files(self, ssh: SshClient):
        ssh.upload_file(self.host.tg_token, self.vm.tg_token_file)
        ssh.upload_file(self.host.tg_chat_id, self.vm.tg_chat_id_file)
        ssh.upload_file(self._create_file(join(self.host.tmp_dir, 'service'), self.vm.my_service()), self.vm.my_service_path)
        ssh.upload_file(self._create_file(join(self.host.tmp_dir, 'script.sh'),self.vm.script_sh()), self.vm.script_path)

    def _start_my_service(self, ssh: SshClient):
        ssh.ssh_exec_commands(f"sudo rm /var/log/journal/*/*.journal")  # clean journal
        ssh.ssh_exec_commands(self.vm.start_service_commands)

    def _create_vm_dirs(self, ssh: SshClient):
        ssh.ssh_exec_commands(f'mkdir {self.vm.tg_dir}')

    def _change_vm_service_dir_access(self, ssh: SshClient):
        ssh.ssh_exec_commands([
            f'sudo chown {self.vm.user}:{self.vm.user} {self.vm.services_dir}',
            f'sudo chmod u+w {self.vm.services_dir}'
        ])

    def _wait_execute_service(self, ssh: SshClient):
        print(f"[red]{'-' * 90}\n|INFO|{self.vm.name}| Wait executing script on vm\n{'-' * 90}")
        ssh.wait_execute_service(self.vm.my_service_name, status=self.test_status)
        ssh.ssh_exec_commands(f'sudo systemctl disable {self.vm.my_service_name}')

    def _download_report(self, ssh: SshClient):
        print(f'[green]|INFO|Download reports dir: {self.vm.report_path}')
        host_report_dir = join(self.host.report_dir, self.version, self.vm.name)
        FileUtils.create_dir(host_report_dir, silence=True)
        try:
            ssh.download_dir(self.vm.report_path, host_report_dir)
        except Exception as e:
            print(f"[red]|WARNING|{self.vm.name}| Exceptions when download report: {e}")

    @staticmethod
    def _create_file(path: str, text: str) -> str:
        FileUtils.file_writer(path, '\n'.join(line.strip() for line in text.split('\n')), newline='')
        return path
