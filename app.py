import curses
from threading import Thread
import time

from dashboard import Dashboard
from website import Website


class App(object):
    def __init__(self, websites_conf):
        self.website_checking_running = False
        self.websites = [Website(website_conf[0], int(website_conf[1])) for website_conf in websites_conf]

    def start(self):
        self.website_checking_running = True
        for website in self.websites:
            thread = Thread(target=App.check_website, args=(website, ), daemon=True)
            thread.start()
            # Daemon threads will stop when app exits

        screen = curses.initscr()
        dashboard = Dashboard(screen, self.websites)
        dashboard.start()
        # curses.wrapper(wrapped_dashboard, self.websites)
        # Thread(target=curses.wrapper, args=(wrapped_dashboard, ))
        print("Exiting")

    def check_website(website):
        while True:
            start = time.time()
            website.check_website()
            time.sleep(max(0, website.check_interval - (time.time() - start)))
