# -*- coding: utf-8 -*-
import time
from os.path import join, dirname, realpath

from frameworks.VBox import VirtualMachine
from frameworks.ssh_client.ssh_client import SshClient


class DesktopTests:
    def __init__(self):
        self.vm = VirtualMachine('Kubuntu')
        self.service_path = join(dirname(realpath(__file__)), 'scripts', 'myscript.service')
        self.script_path = join(dirname(realpath(__file__)), 'scripts', 'script.sh')

    def run(self):
        ssh = SshClient('192.168.0.114')
        ssh.connect('l02')
        ssh.create_ssh_chanel()
        ssh.upload_file(self.service_path,  '/etc/systemd/system/myscript.service')
        ssh.upload_file(self.script_path, '/home/l02/script.sh')
        ssh.ssh_exec('chmod +x /home/l02/script.sh')
        ssh.ssh_exec('echo 2281500662 | sudo -S systemctl daemon-reload')
        ssh.ssh_exec('sudo systemctl enable myscript.service')
        ssh.ssh_exec("sudo systemctl start myscript.service")
        while ssh.exec_command('systemctl is-active myscript.service') == 'active':
            print('active')
            time.sleep(2)
