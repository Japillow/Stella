from urllib.parse import urlparse

from helpers import ping, contact_web_page
from stats import HttpStats, PingStats


class Website(object):
    def __init__(self, website_url, check_interval):
        self.url = website_url
        parsed_url = urlparse(website_url)
        self.hostname = parsed_url.netloc
        # self.check_interval = check_interval
        self.ping_stats = PingStats(check_interval, 120)
        self.site_stats = HttpStats(check_interval, 120)

    def ping(self):

        is_up, response_time, response_code = ping(self.hostname)
        self.ping_stats.update(is_up, response_time, response_code)

        # if is_up:
        #     print(f"{self.hostname} ping successful")
        # else:
        #     print(f"{self.hostname} ping failed")
        #     self.ping_stats.update(False, None, response_code)

    def contact(self):
        is_up, response_time, response_code = contact_web_page(self.url)
        self.site_stats.update(is_up, response_time, response_code)

        # if is_up:
        #     print(f"{self.url} is up")
        # else:
        #     print(f"{self.url} is down")
