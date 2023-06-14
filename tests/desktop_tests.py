# -*- coding: utf-8 -*-
import os.path
import time
from os.path import join, dirname, realpath

from frameworks.VBox import VirtualMachine
from frameworks.host_control import FileUtils, HostInfo
from frameworks.report import Report
from frameworks.ssh_client.ssh_client import SshClient
from rich.console import Console
console = Console()

class DesktopTests:
    def __init__(self, version: str):
        self.config = FileUtils.read_json(join(os.getcwd(), 'config.json'))
        self.version = version
        self.service_path = join(dirname(realpath(__file__)), 'scripts', 'myscript.service')
        self.script_path = join(dirname(realpath(__file__)), 'scripts', 'script.sh')
        self.token = join(os.path.expanduser('~'), '.telegram', 'token')
        self.chat = join(os.path.expanduser('~'), '.telegram', 'chat')
        self.report_name = f'{self.version}_{HostInfo().name(pretty=True)}_desktop_report.csv'
        self.report = f'/home/l02/scripts/oo_desktop_testing/reports/{self.report_name}'
        self.report_dir = join(os.getcwd(), 'reports')
        FileUtils.create_dir(self.report_dir)

    def run(self):
        for machine_name in self.config['hosts']:
            vm = VirtualMachine(machine_name)
            if vm.check_status():
                vm.stop()
            vm.restore_snapshot()
            vm.run(headless=True)
            vm.wait_net_up()
            self.run_script(vm.get_ip(), 'l02')
            vm.stop()

    def _merge_reports(self):
        reports = FileUtils.get_paths(self.report_dir, name_include=f"{self.version}")
        print(reports)
        Report().merge(reports,  join(self.report_dir, f"{self.version}_full_report.csv"))

    def run_script(self, host_ip:str, user:str):
        ssh = SshClient(host_ip)
        ssh.connect(user)
        ssh.ssh_exec('mkdir /home/l02/.telegram')
        self._upload_files(ssh)
        ssh.ssh_exec_commands([
            'chmod +x /home/l02/script.sh',
            'sudo systemctl daemon-reload',
            "sudo systemctl start myscript.service"
        ])
        self._wait_execute_script(ssh)
        self._download_report(ssh)

    def _upload_files(self, ssh):
        ssh.upload_file(self.token, '/home/l02/.telegram/token')
        ssh.upload_file(self.chat, '/home/l02/.telegram/chat')
        ssh.upload_file(self.service_path, '/etc/systemd/system/myscript.service')
        ssh.upload_file(self.create_script_sh(), '/home/l02/script.sh')

    @staticmethod
    def _wait_execute_script(ssh):
        with console.status("[red]Waiting for execute script") as status:
            while ssh.exec_command('systemctl is-active myscript.service') == 'active':
                status.update(ssh.exec_command('journalctl -n 20 -u myscript.service'))
                time.sleep(0.1)
        print(ssh.exec_command('journalctl -b -1 -u myscript.service'))

    def _download_report(self, ssh: SshClient):
        try:
            ssh.download_file(self.report, join(self.report_dir, self.report_name))
        except Exception as e:
            print(f"Exceptions when download report: {e}")

    def create_script_sh(self) -> str:
        script_content = f'''\
        #!/usr/bin/bash
        cd ~/scripts/oo_desktop_testing
        git pull
        source ~/scripts/oo_desktop_testing/.venv/bin/activate
        inv desktop -v {self.version}\
        '''
        FileUtils.file_writer(self.script_path, '\n'.join(line.strip() for line in script_content.split('\n')))
        return self.script_path
