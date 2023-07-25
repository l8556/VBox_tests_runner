# -*- coding: utf-8 -*-
import time
import concurrent.futures
import signal

from tests.desktop_tests import DesktopTests


def handle_interrupt(signum, frame):
    print("[bold red]|WARNING| Interruption by the user")
    raise KeyboardInterrupt

signal.signal(signal.SIGINT, handle_interrupt)

def run_test(version, vm_name):
    DesktopTests(version=version, vm_name=vm_name, status_bar=False).run()

def run(version, vm_names: list, max_processes: int = 1, run_timeout: int | float = 0):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_processes) as executor:
        try:
            futures = []
            for vm_name in vm_names:
                futures.append(executor.submit(run_test, version, vm_name))
                time.sleep(run_timeout)
            done, not_done = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_EXCEPTION)
            for future in done:
                if future.exception():
                    print(
                        f"[bold red]{'-'*90}\n|ERROR| Exceptions when execute the process:"
                        f"{future.exception()}\n{'-'*90}\n\n"
                    )
            for future in not_done:
                future.cancel()
        except KeyboardInterrupt:
            print("[bold red]|WARNING| Interruption by the user")
            executor.shutdown(wait=False, cancel_futures=True)
