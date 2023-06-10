# -*- coding: utf-8 -*-
from os.path import join, expanduser


class SshData:
    default_ssh_key: str = join(expanduser("~"), '.ssh', 'id_rsa.pub')