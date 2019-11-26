import curses
from threading import Lock
from threading import Thread
import time

from stella import config
from stella.dashboard import Dashboard
from stella.website import Website


class App(object):
    def __init__(self, websites_conf):
        """Returns a website monitoring console app.

        The app is able to monitor websites and display a console
        with computed stats based on the website monitoring.

        Parameters
        ----------
        websites_conf : list
            list of website urls to monitor along with the interval at which to monitor.
            Format is [(url, interval), ...]

        Attributes
        ----------
        websites : list
            list of Website objects used to monitor and compute stats for each website
        alert_history : list
            list of Alert objects representing the app alert history
        """

        self.websites = [Website(website_conf[0], int(website_conf[1])) for website_conf in websites_conf]
        self.alert_history = []
        self.alert_history_lock = Lock()

    def wrapped_dashboard(self, screen):
        """Dashboard wrapper used to resume terminal state in case of a program crash.

        Used for developement purposes
        """
        dashboard = Dashboard(screen, self.websites, self.alert_history)
        dashboard.start()

    def start(self):
        """Start the monitoring threads and the console dashboard"""
        for website in self.websites:
            thread = Thread(target=App.monitor_website,
                            args=(website, self.alert_history, self.alert_history_lock),
                            daemon=True)
            thread.start()
            # Daemon threads will stop when program exits

        # Start Dashboard
        # Dashboard is started in the main thread since POSIX signals cannot be handled in children threads
        curses.wrapper(self.wrapped_dashboard)

        # When dashboard is exited, program will end and exit.

    def monitor_website(website, alert_history, alert_history_lock=Lock()):
        """Regularly check whether the site is up, and update stats and alert status accordingly.

        This function is an infinite loop. Run inside a thread to prevent blocking the program.

        Arguments
        ---------
        website : website.Website
            The website to monitor. It can be a shared object, but
            ensure all uses of the website attributes are protected by the website.lock attribute
        alert_history : list
            An shared object used to save the alerts if any are detected
        alert_history_lock : threading.Lock
            a lock to ensure alert_history is only used by one website at a time


        Note
        ----
        Arguments are shared attributes. Ensure they are correctly protected by the respective thread locks.
        """
        while True:
            start = time.time()

            if config.MONITOR_HTTP_RATHER_THAN_ICMP:
                website.http_ping_and_update_http_stats()
                alert = website.check_http_stats_for_alert()
            else:
                website.ping_and_update_ping_stats()
                alert = website.check_ping_stats_for_alert()

            if alert is not None:
                alert_history_lock.acquire()
                alert_history += [alert]
                alert_history_lock.release()

            time.sleep(max(0, website.check_interval - (time.time() - start)))
