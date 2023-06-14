# -*- coding: utf-8 -*-
from platform import system, machine, version
from rich import print

from frameworks.decorators.decorators import singleton
from .Unix import Unix


@singleton
class HostInfo:
    def __init__(self):
        self.os = system().lower()
        self.__arch = machine().lower()

    def name(self, pretty: bool = False) -> str | None:
        return self.os if self.os == 'windows' else Unix().pretty_name if pretty else Unix().id

    @property
    def version(self) -> str | None:
        return version() if self.os == 'windows' else Unix().version

    @property
    def os(self):
        return self.__os

    @property
    def arch(self):
        return self.__arch

    @os.setter
    def os(self, value):
        match value:
            case 'linux':
                self.__os = 'linux'
            case 'darwin':
                self.__os = 'mac'
            case 'windows':
                self.__os = 'windows'
            case definition_os:
                print(f"[bold red]|WARNING| Error defining os: {definition_os}")
