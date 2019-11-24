import curses
import curses.ascii
from signal import signal, SIGINT, SIGTERM
import sys


def wrapped_dashboard(screen, websites):
    print("Starting Dashboard")
    dashboard = Dashboard(screen, websites)
    dashboard.start()


class Dashboard(object):
    def __init__(self, screen, websites):
        signal(SIGINT, self.stop)
        signal(SIGTERM, self.stop)
        self.screen = screen
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.curs_set(False)
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
        self.screen.keypad(True)
        self.websites = websites
        self.selected_website = 0

    def start(self):
        self.init_screen()
        cont = True
        while cont:
            self.home_screen()
            cont = self.listen_for_input()

    def stop(self, _, __):
        self.screen.keypad(False)
        curses.curs_set(True)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        sys.exit(0)

    def init_screen(self):
        self.screen.clear()
        self.screen.refresh()
        self.window = curses.newwin(100, 100, 0, 1)

    def home_screen(self):
        self.window.addstr(
            0, 0, "Select a website to display additional information (press H for help):")

        for i, website in enumerate(self.websites):
            if i == self.selected_website:
                self.window.addstr(i + 1, 0, f"> {website.hostname}",
                                   curses.color_pair(1) | curses.A_BOLD)
            else:
                self.window.addstr(i + 1, 0, f"  {website.hostname}")

        self.window.refresh()

        # websites_choice_pad = curses.newpad(100, 100)
        # # websites_choice_pad.border('|', '|', '-', '-', '+', '+', '+', '+')

        # # websites_info_pad = curses.newpad(100, 100)
        # for i, website in enumerate(self.websites):
        #     if i == self.selected_website:
        #         websites_choice_pad.addstr(i, 0, f"> {website.hostname}", curses.color_pair(1) | curses.A_BOLD)
        #     else:
        #         websites_choice_pad.addstr(i, 0, f"  {website.hostname}")
        # websites_choice_pad.refresh(0, 0, 2, 1, 25, 50)

    def listen_for_input(self):
        try:
            char_ord = self.screen.getch()
            char = chr(char_ord).upper()

            self.window.clear()
            self.window.refresh()

            if char == 'Q' or char_ord == curses.ascii.ESC:
                return False
            elif char == 'H':
                self.print_help_screen()
            elif char_ord == curses.KEY_DOWN:
                if self.selected_website < len(self.websites) - 1:
                    self.selected_website += 1
            elif char_ord == curses.KEY_UP:
                if self.selected_website > 0:
                    self.selected_website -= 1
            elif char_ord == curses.ascii.LF or char_ord == curses.KEY_RIGHT:
                self.print_website_page(self.websites[self.selected_website])
        except Exception:
            self.screen.addstr(0, 0, 'Invalid keypress detected.')
            self.screen.refresh()
            self.screen.getch()
            self.screen.clear()
            self.screen.refresh()
        return True

    def print_help_screen(self):
        self.window.addstr(0, 0, "Help information:")
        self.window.addstr(2, 0, "  H - This help screen")
        self.window.addstr(3, 0, "  Q or ESC - Quit the program")
        self.window.addstr(4, 0, "  Down - Move selection down")
        self.window.addstr(5, 0, "  Up - Move selection up")
        self.window.addstr(6, 0, "  Right or Enter - Select website to check")
        self.window.addstr(8, 0, "Press any key to continue")

        # Wait for any key press
        self.window.getch()
        self.window.clear()
        self.window.refresh()

    def print_website_page(self, website):
        self.screen.addstr(0, 0, f"Website : {website.hostname}")
        self.screen.getch()
        self.screen.clear()
        self.screen.refresh()
