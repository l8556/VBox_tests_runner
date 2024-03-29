# -*- coding: utf-8 -*-
from os import getcwd
from typing import Dict

from dataclasses import dataclass
from os.path import join, isfile, expanduser
from host_tools import File

from frameworks.console import MyConsole

console = MyConsole().console
print = console.print

@dataclass
class TestData:
    version: str
    config_path: str
    project_dir: str = join(getcwd())
    tg_dir: str = join(expanduser('~'), '.telegram')
    tmp_dir: str = join(project_dir, 'tmp')
    know_hosts: str = join(expanduser('~'), '.ssh', 'known_hosts')
    lic_file: str = join(project_dir, 'test_lic.lickey')
    proxy_config_path: str = join(expanduser('~'), '.telegram', 'proxy.json')
    status_bar: bool = True
    telegram: bool = False
    custom_config_mode: bool = False
    update_from: str = None

    def __post_init__(self):
        self.config: Dict = self._read_config()
        self.vm_names: list = self.config.get('hosts', [])
        self.title: str = self.config.get('title', 'Undefined_title')
        self.report_dir: str = join(self.project_dir, 'reports', self.title, self.version)
        self.report_path: str = join(self.report_dir, f"{self.version}_{self.title}_desktop_tests_report.csv")

    @property
    def tg_token(self) -> str:
        return File.read(self.token_file).strip()

    @property
    def token_file(self):
        token_filename = self.config.get('token_file').strip()
        if token_filename:
            file_path = join(self.tg_dir, token_filename)
            if isfile(file_path):
                return file_path
            print(f"[red]|WARNING| Telegram Token from config file not exists: {file_path}")
        return join(self.tg_dir, 'token')

    @property
    def tg_chat_id(self) -> str:
        return File.read(self.chat_id_file).strip()

    @property
    def chat_id_file(self) -> str:
        chat_id_filename = self.config.get('chat_id_file').strip()
        if chat_id_filename:
            file_path = join(self.tg_dir, chat_id_filename)
            if isfile(file_path):
                return file_path
            print(f"[red]|WARNING| Telegram Chat id from config file not exists: {file_path}")
        return join(self.tg_dir, 'chat')

    def _read_config(self):
        if not isfile(self.config_path):
            raise FileNotFoundError(f"[red]|ERROR| Configuration file not found: {self.config_path}")
        return File.read_json(self.config_path)
