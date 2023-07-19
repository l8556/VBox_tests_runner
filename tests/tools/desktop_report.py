# -*- coding: utf-8 -*-
from os.path import join, isfile, basename, dirname
import pandas as pd

from frameworks.host_control import FileUtils
from frameworks.report import Report


class DesktopReport:
    def __init__(self, version: str, report_dir: str):
        self.version = version
        self.dir = report_dir
        self.path = join(self.dir, f"{version}_desktop_runer_report.csv")
        FileUtils.create_dir(self.dir, silence=True)

    def write(self, vm_name: str, exit_code: str):
        self._write_titles() if not isfile(self.path) else ...
        self._writer(self.path, 'a', ["", vm_name, self.version, "", exit_code])

    def get_full(self, title_report: str) -> str:
        paths = FileUtils.get_paths(self.dir, name_include=f"{self.version}", extension='csv')
        full_report = join(self.dir, f"{self.version}_{title_report if title_report else ''}_full_report.csv")
        FileUtils.delete(full_report, silence=True) if isfile(full_report) else ...
        self._handle_results(paths)
        Report().merge(paths, full_report)
        return full_report

    @staticmethod
    def _handle_results(paths: list):
        for report_path in paths if paths else []:
            df = pd.read_csv(report_path)
            df['Vm_name'] = df.apply(lambda row: f"{row['Os']} {row['Version']}", axis=1)
            df.at[0, 'Vm_name'] = basename(dirname(report_path))
            df.to_csv(report_path, index=False, mode='a')

    @staticmethod
    def _writer(file_path: str, mode: str, message: list, delimiter='\t', encoding='utf-8'):
        Report.write(file_path, mode, message, delimiter, encoding)

    def _write_titles(self):
        self._writer(self.path, 'w', ['Os', 'Vm_name', 'Version', 'Package_name', 'Exit_code'])
