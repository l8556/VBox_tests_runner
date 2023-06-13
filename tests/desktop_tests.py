# -*- coding: utf-8 -*-
import os.path
import time
from os.path import join, dirname, realpath

from rich.progress import track

from frameworks.VBox import VirtualMachine
from frameworks.host_control import FileUtils
from frameworks.ssh_client.ssh_client import SshClient


class DesktopTests:
    def __init__(self, version: str):
        self.version = version
        self.vm = VirtualMachine('Kubuntu')
        self.service_path = join(dirname(realpath(__file__)), 'scripts', 'myscript.service')
        self.script_path = join(dirname(realpath(__file__)), 'scripts', 'script.sh')
        self.token = join(os.path.expanduser('~'), '.telegram', 'token')
        self.chat = join(os.path.expanduser('~'), '.telegram', 'chat')


    def run(self):
        # if self.vm.check_status():
        #     self.vm.stop()
        # self.vm.restore_snapshot()
        # self.vm.run()
        self.run_script()
        # self.vm.stop()

    def run_script(self):
        self.create_script_sh()
        ssh = SshClient('192.168.0.114')
        ssh.connect('l02')
        ssh.ssh_exec('mkdir /home/l02/.telegram')
        ssh.upload_file(self.token, '/home/l02/.telegram/token')
        ssh.upload_file(self.chat, '/home/l02/.telegram/chat')
        ssh.upload_file(self.service_path, '/etc/systemd/system/myscript.service')
        ssh.upload_file(self.script_path, '/home/l02/script.sh')
        ssh.ssh_exec_commands([
            'chmod +x /home/l02/script.sh',
            'sudo systemctl daemon-reload',
            "sudo systemctl start myscript.service"
        ])
        while ssh.exec_command('systemctl is-active myscript.service') == 'active':
            time.sleep(5)

    def create_script_sh(self):
        script_content = f'''#!/usr/bin/bash
        cd /home/l02/scripts/oo_desktop_testing
        source ~/.cache/pypoetry/virtualenvs/oo-desktop-testing-m1OQCp06-py3.10/bin/activate
        inv desktop -v {self.version}
        '''
        with open(self.script_path, 'w', newline='') as file:
            file.write('\n'.join(line.strip() for line in script_content.split('\n')))
