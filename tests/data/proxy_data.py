# -*- coding: utf-8 -*-
from dataclasses import dataclass
from os.path import isfile, join, expanduser

from host_tools import File
from telegram import Proxy


@dataclass
class ProxyData:
    proxy_config_path: str = join(expanduser('~'), '.proxy', 'config.json')

    def __post_init__(self):
        self.config: Proxy | None = self._get_proxy_config()

    def _get_proxy_config(self) -> Proxy | None:
        if isfile(self.proxy_config_path):
            config = File.read_json(self.proxy_config_path)
            return Proxy(config['login'], config['password'], config['ip'], config['port'])
        return None
