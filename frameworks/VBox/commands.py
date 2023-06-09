# -*- coding: utf-8 -*-
from dataclasses import dataclass

@dataclass(frozen=True)
class Commands:
    vboxmanage: str = 'vboxmanage'
    list: str = f'{vboxmanage} list vms'
    snapshot: str = f'{vboxmanage} snapshot'
    modifyvm: str = f'{vboxmanage} modifyvm'
    controlvm: str = f'{vboxmanage} controlvm'
    startvm: str = f'{vboxmanage} startvm'
    showvminfo: str = f'{vboxmanage} showvminfo'
