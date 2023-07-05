# -*- coding: utf-8 -*-
from os.path import join

from frameworks.host_control import FileUtils
from frameworks.report import Report


class DesktopReport:
    def __init__(self, version, report_dir):
        self.version = version
        self.dir = report_dir
        self.path = join(self.dir, f"{version}_desktop_runer_report.csv")
        FileUtils.create_dir(self.dir, silence=True)
        self._writer(self.path, 'w', ['Os', 'VM Name', 'Version', 'Package_name', 'Exit_code'])

    def write(self, os: str,  exit_code: str):
        self._writer(self.path, 'a', [os, self.version, "Nan", exit_code])

    @staticmethod
    def _writer(file_path: str, mode: str, message: list, delimiter='\t', encoding='utf-8'):
        Report.write(file_path, mode, message, delimiter, encoding)
