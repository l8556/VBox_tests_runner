# -*- coding: utf-8 -*-
import time

from frameworks.VBox import VirtualMachine
from frameworks.ssh_client.ssh_client import SshClient


class DesktopTests:
    def __init__(self):
        self.vm = VirtualMachine('Kubuntu')

    def run(self):
        ssh = SshClient('192.168.0.114')
        ssh.connect('l02')
        ssh.create_ssh_chanel()
        ssh.upload_file('/Users/lamb/scripts/VBox_control/scripts/myscript.service',  '/lib/systemd/system/myscript.service')
        ssh.upload_file('/Users/lamb/scripts/VBox_control/scripts/script.sh', '/home/l02/script.sh')
        ssh.ssh_exec('chmod +x /home/l02/script.sh')
        ssh.ssh_exec('echo 2281500662 | sudo -S systemctl daemon-reload')
        ssh.ssh_exec('sudo systemctl enable myscript.service')
        ssh.ssh_exec("sudo systemctl start myscript.service")
        # ssh.ssh_exec('./script.sh')
        time.sleep(15)
        ssh.read_output()

        # '/lib/systemd/system/myscript.service'



        # self.vm.run()
        # self.vm.status()

