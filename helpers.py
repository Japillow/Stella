import platform
import re
import subprocess
import time
from urllib.request import urlopen


def read_websites(file_path):
    """Returns a list of [url, check_interval] for each website."""
    with open(file_path, 'r') as file_handle:
        return [site_url.strip('\n').split(' ') for site_url in file_handle.readlines()]


def ping(host):
    param = '-n' if platform.system() == "Windows" else '-c'
    command = ['ping', param, '1', host]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    response_time = None
    if result.returncode == 0:
        re_search = re.findall("time=[0-9]*.[0-9]* *ms", str(result.stdout))
        if len(re_search) != 1:
            raise RuntimeError("Could not extract time from ping command")
        str_time = re_search[0].strip("time=").strip("ms").strip(" ")
        response_time = float(str_time)
    return (result.returncode == 0, response_time, result.returncode)


def contact_web_page(url):
    try:
        start = time.time()
        response = urlopen(url)
        response_time = time.time() - start
        return True, response_time / 100, response.getcode()

    except Exception:
        return False, None, None
