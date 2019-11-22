import os
import platform
import subprocess


def read_websites(file_path):
    with open(file_path, 'r') as file_handle:
        return [site_url.strip('\n') for site_url in file_handle.readlines()]


def ping(host):
    param = '-n' if platform.system() == "Windows" else '-c'
    command = ['ping', param, '1', host]
    with open(os.devnull, "w") as out:
        exit_code = subprocess.call(command, stdout=out, stderr=out)
    return exit_code == 0
