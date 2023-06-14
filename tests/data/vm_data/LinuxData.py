# -*- coding: utf-8 -*-
from dataclasses import dataclass

from .vm_data import VmData


@dataclass
class LinuxData(VmData):
    def __post_init__(self):
        if not self.user or not self.version or not self.name or not self.ip:
            raise ValueError("User, version, name, ip is a required parameter.")
        self.home_dir = f'/home/{self.user}'
        self.script_path = f'{self.home_dir}/script.sh'
        self.desktop_script_dir = f"{self.home_dir}/scripts/oo_desktop_testing"
        self.venv_path =  f"{self.desktop_script_dir}/.venv/bin/activate"
        self.report_path = f'{self.desktop_script_dir}/reports/{self.version}_desktop_report.csv',
        self.tg_dir = f"{self.home_dir}/.telegram"
        self.tg_token_file = f"{self.tg_dir}/token"
        self.tg_chat_id_file = f"{self.tg_dir}/chat"
        self.services_dir = '/etc/systemd/system'
        self.my_service_name = 'myscript.service'
        self.my_service_path = f'{self.services_dir}/{self.my_service_name}'

    @property
    def start_service_commands(self) -> list:
        return [
            f"sudo journalctl -u {self.my_service_name} --vacuum-size=0",
            f'chmod +x {self.script_path}',
            'sudo systemctl daemon-reload',
            f'sudo systemctl start {self.my_service_name}'
        ]

    def my_service(self):
        return f'''\
        [Unit]
        Description=CustomBashScript

        [Service]
        Type=simple
        ExecStart=/usr/bin/bash {self.script_path}
        User={self.user}

        [Install]
        WantedBy=multi-user.target\
        '''

    def script_sh(self) -> str:
        return f'''\
        #!/usr/bin/bash
        cd {self.desktop_script_dir}
        git pull
        source {self.venv_path}
        inv desktop -v {self.version}\
        '''

