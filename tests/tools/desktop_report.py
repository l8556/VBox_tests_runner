# -*- coding: utf-8 -*-
from os.path import join, isfile
import pandas as pd

from frameworks.host_control import FileUtils
from frameworks.report import Report


class DesktopReport:
    def __init__(self, version: str, report_dir: str):
        self.version = version
        self.dir = report_dir
        self.path = join(self.dir, f"{version}_desktop_runer_report.csv")
        self.report = Report()
        FileUtils.create_dir(self.dir, silence=True)

    def write(self, vm_name: str, exit_code: str):
        self._write_titles() if not isfile(self.path) else ...
        self._writer(self.path, 'a', ["", vm_name, self.version, "", exit_code])

    def get_total_count_os(self, csv_path: str) -> int:
        return self.report.total_count(self.report.read(csv_path), 'Os')

    def all_is_passed(self, csv_path: str) -> bool:
        df = self.report.read(csv_path)
        return df['Exit_code'].eq('Passed').all()

    def get_full(self, title_report: str) -> str:
        report_path = join(self.dir, f"{self.version}_{title_report if title_report else ''}_full_report.csv")
        FileUtils.delete(report_path, silence=True) if isfile(report_path) else ...
        self.report.merge(
            FileUtils.get_paths(self.dir, name_include=f"{self.version}", extension='csv'),
            report_path
        )
        return report_path

    def insert_vm_name(self, csv_path: str, vm_name: str) -> None:
        self.report.save_csv(
            self.report.insert_column(csv_path, location='Version', column_name='Vm_name', value=vm_name),
            csv_path
        )

    def _writer(self, file_path: str, mode: str, message: list, delimiter='\t', encoding='utf-8'):
        self.report.write(file_path, mode, message, delimiter, encoding)

    def _write_titles(self):
        self._writer(self.path, 'w', ['Os', 'Vm_name', 'Version', 'Package_name', 'Exit_code'])
