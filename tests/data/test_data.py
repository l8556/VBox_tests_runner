# -*- coding: utf-8 -*-
import json
import os
from dataclasses import dataclass
from os.path import join, isfile
from frameworks.host_control import FileUtils
from frameworks.console import MyConsole
from frameworks.telegram import Telegram

console = MyConsole().console
print = console.print

@dataclass(frozen=True)
class TestData:
    version: str
    config_path: str
    project_dir: str = join(os.getcwd())
    tg_dir: str = join(os.path.expanduser('~'), '.telegram')
    tmp_dir: str = join(project_dir, 'tmp')
    lic_file: str = join(project_dir, 'test_lic.lickey')
    status_bar: bool = True
    telegram: bool = False
    custom_config_mode: bool = False

    @property
    def tg(self):
        return Telegram(token_path=self.tg_token, chat_id_path=self.tg_chat_id, tmp_dir=self.tmp_dir)

    @property
    def title(self) -> str:
        title = self.config.get('title')
        if title:
            return title
        print(f"[red]|WARNING| Please fill in the title parameter in the configuration file")
        return 'Undefined_title'

    @property
    def complete_test_msg(self) -> str:
        return f"{self.config.get('title')} desktop editor tests completed on version: {self.version}"

    @property
    def vm_names(self) -> list:
        return self.config['hosts']

    @property
    def report_dir(self) -> str:
        return join(self.project_dir, 'reports', self.config.get('title'), self.version)

    @property
    def config(self) -> json:
        return FileUtils.read_json(self.config_path)

    @property
    def tg_token(self) -> str:
        token_filename = self.config.get('token_file').strip()
        if token_filename:
            file_path = join(self.tg_dir, token_filename)
            if isfile(file_path):
                return file_path
            print(f"[red]|WARNING| Telegram Token from config file not exists: {file_path}")
        return join(self.tg_dir, 'token')

    @property
    def tg_chat_id(self) -> str:
        chat_id_filename = self.config.get('chat_id_file').strip()
        if chat_id_filename:
            file_path = join(self.tg_dir, chat_id_filename)
            if isfile(file_path):
                return file_path
            print(f"[red]|WARNING| Telegram Chat id from config file not exists: {file_path}")
        return join(self.tg_dir, 'chat')
