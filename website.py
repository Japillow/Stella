from threading import Lock
from urllib.parse import urlparse

from Alert import AvailabilityAlert, AvailabilityRecovered
import config
from helpers import http_ping, ping
from stats import HttpStats, PingStats


class Website(object):
    def __init__(self, website_url, check_interval):
        self.lock = Lock()
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

        self.lock.acquire()
        for timeframe in self.ping_stats_list:
            self.ping_stats_list[timeframe].update(is_up, response_time, response_code)
        self.lock.release()

    def contact_website(self):
        is_up, response_time, response_code = http_ping(self.url)

        self.lock.acquire()
        for timeframe in self.http_stats_list:
            self.http_stats_list[timeframe].update(is_up, response_time, response_code)
        self.lock.release()

    def check_website(self):
        self.ping()
        self.contact_website()

    def check_http_availability(self):
        self.lock.acquire()
        availability = self.ping_stats_list[120].availability
        if self.availability_issue and availability > 0.8:
            self.availability_issue = False
            alert = AvailabilityRecovered(self.hostname, availability)
            self.alert_history += [alert]
        if availability < 0.8 and not self.availability_issue:
            self.availability_issue = True
            alert = AvailabilityAlert(self.hostname, availability)
            self.alert_history += [alert]
        else:
            alert = None
        self.lock.release()
        return alert
