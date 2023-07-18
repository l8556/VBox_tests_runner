# -*- coding: utf-8 -*-
from os.path import join, isfile

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

    def merge_reports(self, title_report: str = None):
        report_name =  f"{self.version}_{title_report if title_report else ''}_full_report.csv"
        full_report = join(self.dir, self.version, report_name)
        FileUtils.delete(full_report, silence=True) if isfile(full_report) else ...
        reports = FileUtils.get_paths(self.dir, name_include=f"{self.version}", extension='csv')
        Report().merge(reports, full_report)
        return full_report
