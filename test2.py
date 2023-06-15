import time

from frameworks.console import MyConsole

console = MyConsole().console
status = console.status('test')
def test2(status):
    for i in range(5):
        status.update('234234')
        time.sleep(1)