from urllib.parse import urlparse

from Alert import AvailabilityAlert, AvailabilityRecovered
import config
from helpers import http_ping, ping
from stats import HttpStats, PingStats


class Website(object):
    def __init__(self, website_url, check_interval):
        self.url = website_url
        parsed_url = urlparse(website_url)
        self.hostname = parsed_url.netloc
        self.check_interval = check_interval
        self.availability_issue = False
        self.alert_history = []

        self.ping_stats_list = {timeframe: PingStats(check_interval, timeframe) for timeframe in config.STATS_TIMEFRAME}
        self.http_stats_list = {timeframe: HttpStats(check_interval, timeframe) for timeframe in config.STATS_TIMEFRAME}

    def ping(self):
        is_up, response_time, response_code = ping(self.hostname)
        for timeframe in self.ping_stats_list:
            self.ping_stats_list[timeframe].update(is_up, response_time, response_code)

        # if is_up:
        #     print(f"{self.hostname} ping successful")
        # else:
        #     print(f"{self.hostname} ping failed")
        #     self.ping_stats.update(False, None, response_code)

    def contact_website(self):
        is_up, response_time, response_code = http_ping(self.url)
        for timeframe in self.http_stats_list:
            self.http_stats_list[timeframe].update(is_up, response_time, response_code)

        # if is_up:
        #     print(f"{self.url} is up")
        # else:
        #     print(f"{self.url} is down")

    def check_website(self):
        self.ping()
        self.contact_website()
        self.check_http_availability()

    def check_http_availability(self):
        availability = self.ping_stats_list[120].availability
        if self.availability_issue and availability > 0.8:
            self.availability_issue = False
            self.alert_history += [AvailabilityRecovered(self.hostname, availability)]
        if availability < 0.8 and not self.availability_issue:
            self.availability_issue = True
            self.alert_history += [AvailabilityAlert(self.hostname, availability)]
