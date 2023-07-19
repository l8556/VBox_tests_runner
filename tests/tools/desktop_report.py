# -*- coding: utf-8 -*-
from os.path import isfile
from os.path import dirname
from rich import print

from frameworks.host_control import FileUtils
from frameworks.report import Report
from frameworks.telegram import Telegram


class DesktopReport:
    def __init__(self, report_path: str):
        self.path = report_path
        self.dir = dirname(self.path)
        self.report = Report()
        FileUtils.create_dir(self.dir, silence=True)

    def write(self, version: str, vm_name: str, exit_code: str) -> None:
        self._write_titles() if not isfile(self.path) else ...
        self._writer(mode='a', message=["", vm_name, version, "", exit_code])

    def get_total_count_os(self) -> int:
        return self.report.total_count(self.report.read(self.path), 'Os')

    def all_is_passed(self) -> bool:
        df = self.report.read(self.path)
        return df['Exit_code'].eq('Passed').all()

    def get_full(self, version: str) -> str:
        FileUtils.delete(self.path, silence=True) if isfile(self.path) else ...
        self.report.merge(
            FileUtils.get_paths(self.dir, name_include=f"{version}", extension='csv'),
            self.path
        )
        return self.path

    def insert_vm_name(self, vm_name: str) -> None:
        self.report.save_csv(
            self.report.insert_column(self.path, location='Version', column_name='Vm_name', value=vm_name),
            self.path
        )

    def column_is_empty(self, column_name: str) -> bool:
        if not self.report.read(self.path)[column_name].count() or not isfile(self.path):
            return True
        return False

    def _writer(self, mode: str, message: list, delimiter='\t', encoding='utf-8'):
        self.report.write(self.path, mode, message, delimiter, encoding)

    def _write_titles(self):
        self._writer(mode='w', message=['Os', 'Vm_name', 'Version', 'Package_name', 'Exit_code'])

    def send_to_tg(self, version: str, title: str, token: str, chat_id: str):
        if not isfile(self.path):
            return print(f"[red]|ERROR| Report for sending to telegram not exists: {self.path}")
        Telegram(token_path=token, chat_id_path=chat_id).send_document(
            self.path,
            caption=f"{title} desktop editor tests completed on version: {version}\n"
                    f"Result: {'`All tests passed`' if self.all_is_passed() else '`Some tests have errors`'}\n"
                    f"Number of tested Os: `{self.get_total_count_os()}`"
        )
