# -*- coding: utf-8 -*-
import json
import os.path
import time
from dataclasses import dataclass, field

from os.path import join, dirname, realpath

from frameworks.VBox import VirtualMachine
from frameworks.host_control import FileUtils, HostInfo
from frameworks.report import Report
from frameworks.ssh_client.ssh_client import SshClient
from rich.console import Console
console = Console()

@dataclass(frozen=True)
class TestData:
    project_dir: str = join(os.getcwd())
    tg_token: str = join(os.path.expanduser('~'), '.telegram', 'token')
    tg_chat_id: str = join(os.path.expanduser('~'), '.telegram', 'chat')
    tmp_dir: str = join(project_dir, 'tmp')
    service_path: str = join(dirname(realpath(__file__)), 'scripts', 'myscript.service')


class DesktopTests:
    def __init__(self, version: str):
        self.testing_hosts = FileUtils.read_json(join(os.getcwd(), 'config.json'))['hosts']
        self.version = version
        self.service_path = TestData.service_path
        self.tmp_dir = TestData.tmp_dir
        self.token = TestData.tg_token
        self.chat = TestData.tg_chat_id
        self.report_dir = join(os.getcwd(), 'reports', self.version)
        self.user = None
        FileUtils.create_dir((self.report_dir, self.tmp_dir), silence=True)

    def run(self):
        for machine_name in self.testing_hosts:
            vm = VirtualMachine(machine_name)
            if vm.check_status():
                vm.stop()
            vm.restore_snapshot()
            vm.run(headless=True)
            vm.wait_net_up()
            self.user = vm.get_logged_user()
            self.run_script(vm.get_ip(), self.user, machine_name)
            vm.stop()
        self._merge_reports()

    def _merge_reports(self):
        reports = FileUtils.get_paths(self.report_dir, name_include=f"{self.version}")
        Report().merge(reports,  join(self.report_dir, f"{self.version}_full_report.csv"))

    def run_script(self, host_ip: str, user: str, machine_name: str):
        ssh = SshClient(host_ip)
        ssh.connect(user)
        ssh.ssh_exec(f'mkdir /home/{self.user}/.telegram')
        self._upload_files(ssh)
        ssh.ssh_exec_commands([
            f'chmod +x /home/{self.user}/script.sh',
            'sudo systemctl daemon-reload',
            "sudo systemctl start myscript.service"
        ])
        self._wait_execute_script(ssh)
        ssh.ssh_exec(f'sudo systemctl disable myscript.service')
        self._download_report(ssh, machine_name)

    def _upload_files(self, ssh):
        ssh.upload_file(self.token, f'/home/{self.user}/.telegram/token')
        ssh.upload_file(self.chat, f'/home/{self.user}/.telegram/chat')
        ssh.ssh_exec_commands([
            f'sudo chown {self.user}:{self.user} /etc/systemd/system/',
            'sudo chmod u+w /etc/systemd/system/'
            ])
        ssh.upload_file(
            self._create_file(join(self.tmp_dir, 'myscript.service'), self._generate_my_service()),
            '/etc/systemd/system/myscript.service'
        )
        ssh.upload_file(
            self._create_file(join(self.tmp_dir, 'script.sh'), self._generate_script_sh()),
            f'/home/{self.user}/script.sh'
        )

    @staticmethod
    def _wait_execute_script(ssh):
        with console.status("[red]Waiting for execute script") as status:
            while ssh.exec_command('systemctl is-active myscript.service') == 'active':
                status.update(ssh.exec_command('journalctl -n 20 -u myscript.service'))
                time.sleep(0.1)
        console.print(ssh.exec_command('journalctl -b -1 -u myscript.service'))

    def _download_report(self, ssh: SshClient, machine_name: str):
        try:
            ssh.download_file(
                f'/home/{self.user}/scripts/oo_desktop_testing/reports/{self.version}_desktop_report.csv',
                join(self.report_dir, f'{self.version}_{machine_name}_desktop_report.csv')
            )
        except Exception as e:
            print(f"Exceptions when download report: {e}")

    def _generate_script_sh(self) -> str:
        return f'''\
        #!/usr/bin/bash
        cd ~/scripts/oo_desktop_testing
        git pull
        source ~/scripts/oo_desktop_testing/.venv/bin/activate
        inv desktop -v {self.version}\
        '''
    def _generate_my_service(self):
        return f'''\
        [Unit]
        Description=CustomBashScript
        
        [Service]
        Type=simple
        ExecStart=/usr/bin/bash /home/{self.user}/script.sh
        User={self.user}
        
        [Install]
        WantedBy=multi-user.target\
        '''

    @staticmethod
    def _create_file(path: str, text: str) -> str:
        FileUtils.file_writer(path, '\n'.join(line.strip() for line in text.split('\n')), newline='')
        return path
