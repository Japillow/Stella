import curses
from threading import Thread, Lock
import time

from dashboard import wrapped_dashboard
from website import Website

alert_history_lock = Lock()


class App(object):
    def __init__(self, websites_conf):
        self.website_checking_running = False
        self.websites = [Website(website_conf[0], int(website_conf[1])) for website_conf in websites_conf]
        self.alert_history = []

    def start(self):
        self.website_checking_running = True
        for website in self.websites:
            thread = Thread(target=App.check_website,
                            args=(website, self.alert_history),
                            daemon=True)
            thread.start()
            # Daemon threads will stop when app exits

        curses.wrapper(wrapped_dashboard, self.websites, self.alert_history)
        # dashboard_thread = Thread(target=curses.wrapper, args=(wrapped_dashboard, self.websites))
        # dashboard_thread.start()
        # dashboard_thread.join()
        print("Exiting")

    def check_website(website, alert_history):
        while True:
            start = time.time()
            website.check_website()
            alert = website.check_http_availability()
            if alert is not None:
                alert_history_lock.acquire()
                alert_history += [alert]
                alert_history_lock.release()
            time.sleep(max(0, website.check_interval - (time.time() - start)))
