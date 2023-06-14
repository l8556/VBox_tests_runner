# -*- coding: utf-8 -*-
from dataclasses import dataclass

@dataclass
class VmData:
    user: str
    ip: str
    name: str
    version: str