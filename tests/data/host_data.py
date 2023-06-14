# -*- coding: utf-8 -*-
import os
from dataclasses import dataclass
from os.path import join


@dataclass(frozen=True)
class HostData:
    project_dir: str = join(os.getcwd())
    tg_token: str = join(os.path.expanduser('~'), '.telegram', 'token')
    tg_chat_id: str = join(os.path.expanduser('~'), '.telegram', 'chat')
    tmp_dir: str = join(project_dir, 'tmp')
    report_dir = join(project_dir, 'reports')
