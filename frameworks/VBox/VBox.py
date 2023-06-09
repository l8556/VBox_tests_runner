from .commands import Commands as cmd
from subprocess import getoutput

class Vbox:
    @staticmethod
    def vm_list() -> list:
        output = getoutput(cmd.list)
        print(output)
        return output.split('\n')
