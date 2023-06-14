from .commands import Commands as cmd
from subprocess import getoutput

class Vbox:
    @staticmethod
    def vm_list() -> list:
        return getoutput(cmd.list).split('\n')
