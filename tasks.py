# -*- coding: utf-8 -*-
from invoke import task

from tests.desktop_tests import DesktopTests

@task
def desktop_run(c):
    DesktopTests().run()
