# -*- coding: utf-8 -*-
from os.path import join, isfile

from frameworks.VBox import VirtualMachine
from frameworks.VBox.virtualmachine import VirtualMachinException
from frameworks.console import MyConsole
from frameworks.host_control import FileUtils
from frameworks.report import Report
from frameworks.ssh_client.ssh_client import SshClient
from frameworks.telegram import Telegram
from tests.data import LinuxData, HostData
from tests.tools.desktop_report import DesktopReport

console = MyConsole().console
print = console.print


class DesktopTests:
    def __init__(
            self,
            version: str,
            vm_name: str,
            config_path: str,
            interactive_status: bool = True,
            telegram: bool = False,
            custom_config: bool = False
    ):
        self.custom_config = custom_config
        self.version = version
        self.vm_name = vm_name
        self.telegram = telegram
        self.host = HostData(config_path=config_path)
        self.report = DesktopReport(version, join(self.host.report_dir, self.version, self.vm_name))
        self.tg = Telegram(token_path=self.host.tg_token, chat_id_path=self.host.tg_chat_id, tmp_dir=self.host.tmp_dir)
        self.interactive_status = console.status('') if interactive_status else None
        FileUtils.create_dir((self.host.report_dir, self.host.tmp_dir), silence=True)
        self.vm = None

    def run(self):
        virtual_machine = VirtualMachine(self.vm_name)
        try:
            self.vm = self._create_vm(self.run_vm(virtual_machine))
            print(self.vm.script_sh())
            self.run_script_on_vm()
        except VirtualMachinException:
            self.report.write(self.vm_name, "FAILED_CREATE_VM")
        finally:
            virtual_machine.stop()

    def run_vm(self, vm: VirtualMachine) -> VirtualMachine:
        if vm.check_status():
            vm.stop()
        vm.restore_snapshot()
        vm.set_cpus(4)
        vm.set_memory(4096)
        vm.audio(False)
        vm.run(headless=True)
        vm.wait_net_up(status_bar=self.interactive_status, timeout=600)
        vm.wait_logged_user(status_bar=self.interactive_status, timeout=600)
        return vm

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
        ssh.upload_file(self._create_file(join(self.host.tmp_dir, 'script.sh'), self.vm.script_sh()), self.vm.script_path)
        ssh.upload_file(self.host.config_path, self.vm.custom_config_path)
        ssh.upload_file(self.host.lic_file, self.vm.lic_file)

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
        ssh.wait_execute_service(self.vm.my_service_name, status_bar=self.interactive_status)

    def _download_report(self, ssh: SshClient):
        print(f'[green]|INFO|Download reports dir: {self.vm.report_path}')
        try:
            ssh.download_dir(self.vm.report_path, self.report.dir)
        except Exception as e:
            self.report.write(self.vm.name, "REPORT_NOT_EXISTS")
            print(f"[red]|ERROR| Can't download report from {self.vm.name}.\nError: {e}")

    @staticmethod
    def _create_file(path: str, text: str) -> str:
        FileUtils.file_writer(path, '\n'.join(line.strip() for line in text.split('\n')), newline='')
        return path

    def _create_vm(self, running_vm: VirtualMachine):
        return LinuxData(
            vm_process=running_vm,
            user=running_vm.get_logged_user(),
            version=self.version,
            ip=running_vm.get_ip(),
            name=self.vm_name,
            telegram=self.telegram,
            custom_config=self.custom_config
        )
