# -*- coding: utf-8 -*-
import signal
from os.path import join

from frameworks.VBox import VirtualMachine
from frameworks.VBox.virtualmachine import VirtualMachinException
from frameworks.console import MyConsole
from frameworks.host_control import FileUtils
from frameworks.ssh_client.ssh_client import SshClient
from tests.data import LinuxData, TestData
from tests.tools.desktop_report import DesktopReport

console = MyConsole().console
print = console.print

def handle_interrupt(signum, frame):
    raise KeyboardInterrupt

signal.signal(signal.SIGINT, handle_interrupt)


class DesktopTests:
    def __init__(self, vm_name: str, test_data: TestData, vm_cpus: int = 4, vm_memory: int = 4096):
        self.vm_cores = vm_cpus
        self.vm_memory = vm_memory
        self.data = test_data
        self.vm_name = vm_name
        self.vm = None
        self.report = DesktopReport(self.data.version, join(self.data.report_dir, self.vm_name))
        FileUtils.create_dir((self.data.report_dir, self.data.tmp_dir), silence=True)

    def run(self):
        virtual_machine = VirtualMachine(self.vm_name)
        try:
            self.run_vm(virtual_machine)
            self.vm = self._create_vm_data(virtual_machine.get_logged_user(), virtual_machine.get_ip())
            self.run_script_on_vm()
        except VirtualMachinException:
            self.report.write(self.vm_name, "FAILED_CREATE_VM")
        except KeyboardInterrupt:
            print("[bold red]|WARNING| Interruption by the user")
        finally:
            virtual_machine.stop()

    def run_vm(self, vm: VirtualMachine) -> VirtualMachine:
        if vm.check_status():
            vm.stop()
        vm.restore_snapshot()
        vm.set_cpus(self.vm_cores)
        vm.set_memory(self.vm_memory)
        vm.audio(False)
        vm.run(headless=True)
        vm.wait_net_up(status_bar=self.data.status_bar, timeout=600)
        vm.wait_logged_user(status_bar=self.data.status_bar, timeout=600)
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
        ssh.upload_file(self.data.tg_token, self.vm.tg_token_file)
        ssh.upload_file(self.data.tg_chat_id, self.vm.tg_chat_id_file)
        ssh.upload_file(self._create_file(join(self.data.tmp_dir, 'service'), self.vm.my_service()), self.vm.my_service_path)
        ssh.upload_file(self._create_file(join(self.data.tmp_dir, 'script.sh'), self.vm.script_sh()), self.vm.script_path)
        ssh.upload_file(self.data.config_path, self.vm.custom_config_path)
        ssh.upload_file(self.data.lic_file, self.vm.lic_file)

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
        ssh.wait_execute_service(self.vm.my_service_name, status_bar=self.data.status_bar)

    def _download_report(self, ssh: SshClient):
        try:
            ssh.download_dir(f"{self.vm.report_path}/{self.data.config.get('title')}/{self.data.version}", self.report.dir)
        except Exception as e:
            self.report.write(self.vm.name, "REPORT_NOT_EXISTS")
            print(f"[red]|ERROR| Can't download report from {self.vm.name}.\nError: {e}")

    @staticmethod
    def _create_file(path: str, text: str) -> str:
        FileUtils.file_writer(path, '\n'.join(line.strip() for line in text.split('\n')), newline='')
        return path

    def _create_vm_data(self, user: str, ip: str):
        return LinuxData(
            user=user,
            ip=ip,
            version=self.data.version,
            name=self.vm_name,
            telegram=self.data.telegram,
            custom_config=self.data.custom_config_mode
        )
