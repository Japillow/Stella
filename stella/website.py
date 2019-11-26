from threading import Lock
from urllib.parse import urlparse

from stella import config
from stella.alert import AvailabilityAlert, AvailabilityRecovered
from stella.helpers import http_ping, ping
from stella.stats import HttpStats, PingStats


class Website(object):
    def __init__(self, website_url, check_interval, timeframes=config.STATS_TIMEFRAMES):
        """Returns a website object containing it's stats for the configured timeframes.

        Parameters
        ----------
        website_url : str
            url of a page of a website to monitor through http.
            hostname is extracted from the url to monitor through icmp.
        check_interval : int
            how often the website must be checked
        timeframes : list(int)
            list of durations for which to compute stats from.

        Attributes
        ----------
        availability_issue : bool
            indicates if an availability alert is currently fired
        ping_stats_list : list of (int: PingStats)
            website icmp stats for each of the timeframes
        http_stats_list : list of (int: HttpStats)
            website http stats for each of the timeframes
        """
        self.lock = Lock()

        self.url = website_url
        parsed_url = urlparse(website_url)
        self.hostname = parsed_url.netloc
        self.check_interval = check_interval

        self.availability_issue = False
        self.alert_history = []

        self.ping_stats_list = {timeframe: PingStats(check_interval, timeframe) for timeframe in timeframes}
        self.http_stats_list = {timeframe: HttpStats(check_interval, timeframe) for timeframe in timeframes}

    def ping_and_update_ping_stats(self):
        """Updates the website ping stats with a new ping request."""
        is_up, response_time, response_code = ping(self.hostname)
        
        self.lock.acquire()
        for timeframe in self.ping_stats_list:
            self.ping_stats_list[timeframe].update(is_up, response_time, response_code)
        self.lock.release()

    def http_ping_and_update_http_stats(self):
        """Updates the website http stats with a new http request."""
        is_up, response_time, response_code = http_ping(self.url)

        self.lock.acquire()
        for timeframe in self.http_stats_list:
            self.http_stats_list[timeframe].update(is_up, response_time, response_code)
        self.lock.release()

    def check_for_alert(self, threshold=0.8, timeframe=120):
        """Checks if an alert should be raised.

        Check is based on a defined threshold and timeframe
        for the icmp ping availability stat metric.
        """
        self.lock.acquire()
        availability = self.ping_stats_list[timeframe].availability
        if self.ping_stats_list[timeframe].timeframe_reached():
            if self.availability_issue and availability > threshold:
                self.availability_issue = False
                alert = AvailabilityRecovered(self.hostname, availability)
                self.alert_history += [alert]
            elif availability < threshold and not self.availability_issue:
                self.availability_issue = True
                alert = AvailabilityAlert(self.hostname, availability)
                self.alert_history += [alert]
            else:
                alert = None
        else:
            alert = None
        self.lock.release()
        return alert
