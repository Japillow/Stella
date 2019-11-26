import platform
import re
import subprocess
from threading import Lock
import time
from urllib.parse import urlparse
from urllib.request import urlopen

from stella.alert import AvailabilityAlert
from stella.alert import AvailabilityRecovered
from stella import config
from stella.stats import HttpStats
from stella.stats import PingStats


class Website(object):
    def __init__(self,
                 website_url,
                 check_interval,
                 timeframes=[config.ALERTING_TIMEFRAME] + config.STATS_TIMEFRAMES,
                 alert_threshold=config.DEFAULT_ALERT_THRESHOLD,
                 alerting_timeframe=config.ALERTING_TIMEFRAME):
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
        alert_threshold : float
            availability threshold for triggerign alerts
        alerting_timeframe : int
            timeframe on which to evaluate website availability
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
        self.alert_threshold = alert_threshold
        self.alerting_timeframe = alerting_timeframe

        self.availability_issue = False
        self.alert_history = []

        self.ping_stats_list = {timeframe: PingStats(check_interval, timeframe) for timeframe in timeframes}
        self.http_stats_list = {timeframe: HttpStats(check_interval, timeframe) for timeframe in timeframes}

    def ping_and_update_ping_stats(self):
        """Updates the website ping stats with a new ping request."""
        is_up, response_time, response_code = Website.ping(self.hostname)

        self.lock.acquire()
        for timeframe in self.ping_stats_list:
            self.ping_stats_list[timeframe].update(is_up, response_time, response_code)
        self.lock.release()

    def http_ping_and_update_http_stats(self):
        """Updates the website http stats with a new http request."""
        is_up, response_time, response_code = Website.http_ping(self.url)

        self.lock.acquire()
        for timeframe in self.http_stats_list:
            self.http_stats_list[timeframe].update(is_up, response_time, response_code)
        self.lock.release()

    def check_ping_stats_for_alert(self):
        """Checks if an alert should be raised.

        Check is based on a defined threshold and timeframe
        for the icmp ping availability stat metric.
        """
        self.lock.acquire()
        alert = self.check_for_alert(self.ping_stats_list)
        self.lock.release()
        return alert

    def check_http_stats_for_alert(self):
        """Checks if an alert should be raised.

        Check is based on a defined threshold and timeframe
        for the http ping availability stat metric.
        """
        self.lock.acquire()
        alert = self.check_for_alert(self.ping_stats_list)
        self.lock.release()
        return alert

    def check_for_alert(self, stats_list):
        """Checks if an alert should be raised based on a Stat list."""

        availability = stats_list[self.alerting_timeframe].availability
        # Ensure enough datapoints are available
        if stats_list[self.alerting_timeframe].timeframe_reached():

            # Firing Alert
            if self.availability_issue and availability >= self.alert_threshold:
                self.availability_issue = False
                alert = AvailabilityRecovered(self.hostname, availability)
                self.alert_history += [alert]

            # Recovering
            elif availability < self.alert_threshold and not self.availability_issue:
                self.availability_issue = True
                alert = AvailabilityAlert(self.hostname, availability)
                self.alert_history += [alert]

            else:
                alert = None
        else:
            alert = None
        return alert

    def ping(host):
        """sends an ICMP ECHO_REQUEST packet to the given host and returns relevant information.

        Returns
        -------
        int : success status
        float : round-trip time (in ms)
        int : ICMP response code
        """

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

    def http_ping(url):
        """Probes the given url and returns relevant information.

        Returns
        -------
        int : success status
        float : response time (in ms)
        int : HTTP response code
        """
        try:
            start = time.time()
            response = urlopen(url)
            response_time = time.time() - start
            return True, response_time * 1000, response.getcode()

        except Exception:
            return False, None, None
