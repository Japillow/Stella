import curses
import curses.ascii
from signal import signal, SIGINT, SIGTERM
import sys


def wrapped_dashboard(screen):
    dashboard = Dashboard(screen)
    dashboard.start()


class Dashboard(object):
    def __init__(self, screen):
        signal(SIGINT, self.stop)
        signal(SIGTERM, self.stop)
        self.screen = screen
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.curs_set(1)
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
        self.screen.keypad(True)
        self.screen.refresh()

    def start(self):
        self.init_screen()
        cont = True
        while cont:
            cont = self.listen_for_input()

    def stop(self, _, __):
        self.screen.keypad(False)
        curses.curs_set(0)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        sys.exit(0)

    def init_screen(self):
        pass

    def listen_for_input(self):
        return False
