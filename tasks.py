# -*- coding: utf-8 -*-
import os
from os.path import join

from invoke import task
from rich.prompt import Prompt

from frameworks.host_control import FileUtils
from tests.desktop_tests import DesktopTests

@task
def desktop_test(c, version=None):
    version = version if version else Prompt.ask('[red]Please enter version')
    DesktopTests(version=version).run()