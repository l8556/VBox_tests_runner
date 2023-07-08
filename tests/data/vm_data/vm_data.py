# -*- coding: utf-8 -*-
import os
from dataclasses import dataclass
from os.path import join

from frameworks.VBox import VirtualMachine
from frameworks.host_control import FileUtils


@dataclass
class VmData:
    vm_process: VirtualMachine
    telegram: bool
    user: str
    ip: str
    name: str
    version: str
    custom_config: bool
    desktop_testing_url: str = FileUtils.read_json(join(os.getcwd(), 'config.json'))['desktop_script']
    branch: str = FileUtils.read_json(join(os.getcwd(), 'config.json'))['branch']
