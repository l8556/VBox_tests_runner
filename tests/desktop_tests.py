# -*- coding: utf-8 -*-
import signal
from os.path import join, dirname, isfile
from typing import Optional

from host_tools.utils import Dir

from frameworks.VBox import VirtualMachine
from frameworks.VBox.virtualmachine import VirtualMachinException
from frameworks.console import MyConsole
from frameworks.decorators import retry
from host_tools import File
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
        Dir.create((self.data.report_dir, self.data.tmp_dir), stdout=False)
        self.report = self._create_report()

    @retry(max_attempts=2, exception_type=VirtualMachinException)
    def run(self, headless: bool = True):
        virtual_machine = VirtualMachine(self.vm_name)
        try:
            self.run_vm(virtual_machine, headless=headless)
            self.vm = self._create_vm_data(virtual_machine.get_logged_user(), virtual_machine.get_ip())
            self._clean_know_hosts(self.vm.ip)
            self.run_script_on_vm(user_password=self._get_user_password(virtual_machine))
        except VirtualMachinException:
            print(f"[bold red]|ERROR|{self.vm_name}| Failed to create  a virtual machine")
            self.report.write(self.data.version, self.vm_name, "FAILED_CREATE_VM")
        except KeyboardInterrupt:
            print("[bold red]|WARNING| Interruption by the user")
            raise
        finally:
            virtual_machine.stop()

    def run_vm(self, vm: VirtualMachine, headless: bool = True) -> VirtualMachine:
        if vm.check_status():
            vm.stop()
        vm.restore_snapshot()
        self.configurate_virtual_machine(vm)
        vm.run(headless=headless)
        vm.wait_net_up(status_bar=self.data.status_bar, timeout=600)
        vm.wait_logged_user(status_bar=self.data.status_bar, timeout=600)
        return vm

    def configurate_virtual_machine(self, vm: VirtualMachine) -> None:
        vm.set_cpus(self.vm_cores)
        vm.nested_virtualization(True)
        vm.set_memory(self.vm_memory)
        vm.audio(False)
        vm.speculative_execution_control(True)

    def run_script_on_vm(self, user_password: str = None):
        ssh = SshClient(self.vm.ip, self.vm.name)
        ssh.connect(self.vm.user, password=user_password)
        self._create_vm_dirs(ssh)
        self._change_vm_service_dir_access(ssh)
        self._upload_files(ssh)
        self._start_my_service(ssh)
        self._wait_execute_service(ssh)
        self._download_report(ssh)

    def _upload_files(self, ssh: SshClient):
        service = self._create_file(join(self.data.tmp_dir, 'service'), self.vm.my_service())
        script = self._create_file(join(self.data.tmp_dir, 'script.sh'), self.vm.script_sh())
        ssh.upload_file(self.data.token_file, self.vm.tg_token_file)
        ssh.upload_file(self.data.chat_id_file, self.vm.tg_chat_id_file)
        ssh.upload_file(self.data.proxy_config_path, self.vm.proxy_config_file)
        ssh.upload_file(service, self.vm.my_service_path)
        ssh.upload_file(script, self.vm.script_path)
        ssh.upload_file(self.data.config_path, self.vm.custom_config_path)
        ssh.upload_file(self.data.lic_file, self.vm.lic_file)

    @staticmethod
    def _create_file(path: str, text: str) -> str:
        File.write(path, '\n'.join(line.strip() for line in text.split('\n')), newline='')
        return path

    def _start_my_service(self, ssh: SshClient):
        ssh.ssh_exec_commands(f"sudo rm /var/log/journal/*/*.journal")  # clean journal
        ssh.ssh_exec_commands(self.vm.start_service_commands)

    def _create_vm_dirs(self, ssh: SshClient):
        ssh.ssh_exec_commands(f'mkdir {self.vm.script_dir}')
        ssh.ssh_exec_commands(f'mkdir {self.vm.tg_dir}')

    def _change_vm_service_dir_access(self, ssh: SshClient):
        ssh.ssh_exec_commands([
            f'sudo chown {self.vm.user}:{self.vm.user} {self.vm.services_dir}',
            f'sudo chmod u+w {self.vm.services_dir}'
        ])

    def _wait_execute_service(self, ssh: SshClient):
        print(f"[bold cyan]{'-' * 90}\n|INFO|{self.vm.name}| Wait executing script on vm\n{'-' * 90}")
        ssh.wait_execute_service(self.vm.my_service_name, status_bar=self.data.status_bar)

    def _download_report(self, ssh: SshClient):
        try:
            ssh.download_dir(f"{self.vm.report_path}/{self.data.title}/{self.data.version}", self.report.dir)
            if self.report.column_is_empty("Os"):
                raise FileNotFoundError
            self.report.insert_vm_name(self.vm_name)
        except (FileExistsError, FileNotFoundError) as e:
            self.report.write(self.data.version, self.vm.name, "REPORT_NOT_EXISTS")
            print(f"[red]|ERROR| Can't download report from {self.vm.name}.\nError: {e}")

    def _create_vm_data(self, user: str, ip: str):
        return LinuxData(
            user=user,
            ip=ip,
            version=self.data.version,
            old_version=self.data.update_from,
            name=self.vm_name,
            telegram=self.data.telegram,
            custom_config=self.data.custom_config_mode
        )

    def _create_report(self):
        return DesktopReport(
            join(self.data.report_dir, self.vm_name, f"{self.data.version}_{self.data.title}_report.csv")
        )

    def _clean_know_hosts(self, ip: str):
        with open(self.data.know_hosts, 'r') as file:
            filtered_lines = [line for line in file.readlines() if not line.startswith(ip)]
        with open(self.data.know_hosts, 'w') as file:
            file.writelines(filtered_lines)

    def _get_user_password(self, vm: VirtualMachine) -> Optional[str]:
        try:
            password_file = join(dirname(vm.get_parameter_info('CfgFile')), 'password')
            password = File.read(password_file).strip() if isfile(password_file) else None
            return password if password else self.data.config.get('password', None)
        except (TypeError, FileNotFoundError):
            return self.data.config.get('password', None)
