# -*- coding: utf-8 -*-
import os
from dataclasses import dataclass
from os.path import join

from frameworks.host_control import FileUtils


@dataclass
class VmData:
    user: str
    ip: str
    name: str
    version: str
    desktop_testing_url: str = FileUtils.read_json(join(os.getcwd(), 'config.json'))['desktop_script']
    branch: str = FileUtils.read_json(join(os.getcwd(), 'config.json'))['branch']
