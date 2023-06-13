# -*- coding: utf-8 -*-
import os
from os.path import join

from invoke import task

from frameworks.host_control import FileUtils
from tests.desktop_tests import DesktopTests

@task
def desktop_test(c, version=None):
    config = FileUtils.read_json(join(os.getcwd(), 'config.json'))
    version = version if version else config['version']
    DesktopTests(version=version).run()
