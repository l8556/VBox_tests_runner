# -*- coding: utf-8 -*-
from invoke import task
from rich.prompt import Prompt
from tests.desktop_tests import DesktopTests

@task
def desktop_test(c, version=None):
    version = version if version else Prompt.ask('[red]Please enter version')
    DesktopTests(version=version).run()