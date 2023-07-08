# -*- coding: utf-8 -*-
import os
from dataclasses import dataclass
from os.path import join, isfile
from frameworks.host_control import FileUtils
from frameworks.console import MyConsole
console = MyConsole().console
print = console.print

@dataclass(frozen=True)
class HostData:
    project_dir: str = join(os.getcwd())
    tg_dir: str = join(os.path.expanduser('~'), '.telegram')
    tmp_dir: str = join(project_dir, 'tmp')
    report_dir: str = join(project_dir, 'reports')
    config_path: str = join(os.getcwd(), 'config.json')
    custom_config: str = join(project_dir, 'custom_coinfigs', 'portal_config.json')

    @property
    def config(self):
        return FileUtils.read_json(self.config_path)

    @property
    def tg_token(self):
        token_filename = self.config.get('token_file').strip()
        if token_filename:
            file_path = join(self.tg_dir, token_filename)
            if isfile(file_path):
                return file_path
            print(f"[red]|WARNING| Token file not exists: {file_path}")
        return join(self.tg_dir, 'token')

    @property
    def tg_chat_id(self):
        chat_id_filename = self.config.get('chat_id_file').strip()
        if chat_id_filename:
            file_path = join(self.tg_dir, chat_id_filename)
            if isfile(file_path):
                return file_path
            print(f"[red]|WARNING| Chat id file not exists: {file_path}")
        return join(self.tg_dir, 'chat')
