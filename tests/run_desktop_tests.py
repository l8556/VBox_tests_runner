# -*- coding: utf-8 -*-
from frameworks.VBox import VirtualMachine


class DesktopTests:
    def __init__(self):
        self.vm = VirtualMachine('Kubuntu')

    def run(self):
        self.vm.run()
        self.vm.status()
