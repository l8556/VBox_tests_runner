# -*- coding: utf-8 -*-
from dataclasses import dataclass
from os.path import basename, splitext

from .vm_data import VmData


@dataclass
class LinuxData(VmData):
    def __post_init__(self):
        if not self.user or not self.version or not self.name or not self.ip:
            raise ValueError("User, version, name, ip is a required parameter.")
        self.home_dir = f'/home/{self.user}'
        self.script_path = f'{self.home_dir}/script.sh'
        self.script_dir = f"{self.home_dir}/scripts"
        self.desktop_testing_path = f"{self.script_dir}/{splitext(basename(self.desktop_testing_url))[0]}"
        self.venv_path = f"{self.desktop_testing_path}/.venv/bin/activate"
        self.report_path = f'{self.desktop_testing_path}/reports/{self.version}'
        self.tg_dir = f"{self.home_dir}/.telegram"
        self.tg_token_file = f"{self.tg_dir}/token"
        self.tg_chat_id_file = f"{self.tg_dir}/chat"
        self.services_dir = '/etc/systemd/system'
        self.my_service_name = 'myscript.service'
        self.my_service_path = f'{self.services_dir}/{self.my_service_name}'

    @property
    def start_service_commands(self) -> list:
        return [
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
        ExecStart=/bin/bash {self.script_path}
        User={self.user}

        [Install]
        WantedBy=multi-user.target\
        '''

    def script_sh(self) -> str:
        return f'''\
        #!/bin/bash
        cd {self.script_dir}
        git clone {'-b ' if self.branch else ''}{self.branch if self.branch else ''} {self.desktop_testing_url}
        cd {self.desktop_testing_path}
        {'/home/l02/.pyenv/versions/3.9.7/bin/python' if self.name == 'Ubuntu16' else 'python3'} -m venv .venv
        source ./.venv/bin/activate
        pip install -r requirements.txt
        invoke desktop-test -v {self.version}\
        '''
