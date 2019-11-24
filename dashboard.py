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
        self.window = curses.newwin(1, 100, 0, 1)
        self.window.addstr(
            0, 0, "Select a website to display additional information (press H for help):")
        self.window.refresh()

        self.window_hostname = curses.newwin(100, 100, 1, 1)
        self.window_availability = curses.newwin(100, 100, 1, 20)
        self.window_response_time = curses.newwin(100, 100, 1, 33)

        self.window_hostname.addstr(0, 0, "Hostname")
        self.window_availability.addstr(0, 0, " Availability")
        self.window_response_time.addstr(0, 0, " Resp.Time (min/avg/max) in ms")

        for i, website in enumerate(self.websites):
            if i == self.selected_website:
                self.window_hostname.addstr(i + 1, 0, f"> {website.hostname}",
                                            curses.color_pair(1) | curses.A_BOLD)
                self.window_availability.addstr(i + 1, 0,
                                                f" {website.ping_stats_list[120].availability:.2f}",
                                                curses.color_pair(1) | curses.A_BOLD)
                self.window_response_time.addstr(
                    i + 1, 0, (f" {website.ping_stats_list[120].min_response_time:.0f}"
                               f"/{website.ping_stats_list[120].average_response_time:.0f}"
                               f"/{website.ping_stats_list[120].max_response_time:.0f}"),
                    curses.color_pair(1) | curses.A_BOLD)

            else:
                self.window_hostname.addstr(i + 1, 0, f"  {website.hostname}")
                self.window_availability.addstr(
                    i + 1, 0, f" {website.ping_stats_list[120].availability:.2f}")
                self.window_response_time.addstr(
                    i + 1, 0, (f" {website.ping_stats_list[120].min_response_time:.0f}"
                               f"/{website.ping_stats_list[120].average_response_time:.0f}"
                               f"/{website.ping_stats_list[120].max_response_time:.0f}"))

        self.window.refresh()
        self.window_hostname.refresh()
        self.window_availability.refresh()
        self.window_response_time.refresh()

    def listen_for_input(self):
        try:
            char_ord = self.screen.getch()
            char = chr(char_ord).upper()

            self.screen.clear()
            self.screen.refresh()

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
        except Exception as exc:
            self.screen.addstr(0, 0, 'An unexpected error occured: ')
            self.screen.addstr(1, 5, f'{exc}')
            self.screen.refresh()
            self.screen.getch()
            self.screen.clear()
            self.screen.refresh()
        return True

    def print_help_screen(self):
        self.window = curses.newwin(9, 50, 0, 1)
        self.window.addstr(0, 0, "Help information:")
        self.window.addstr(2, 0, "  H - This help screen")
        self.window.addstr(3, 0, "  Q or ESC - Quit the program")
        self.window.addstr(4, 0, "  Down - Move selection down")
        self.window.addstr(5, 0, "  Up - Move selection up")
        self.window.addstr(6, 0, "  Right or Enter - Select website to check")
        self.window.addstr(8, 0, "Press any key to continue")

        # Wait for any key press
        self.window.getch()
        self.screen.clear()
        self.screen.refresh()

    def print_website_page(self, website):
        self.window = curses.newwin(50, 50, 0, 1)
        self.window.addstr(0, 0, f"Website : {website.hostname}", curses.A_BOLD)
        print_index = self.print_detailed_website_stats(self.window, 1,
                                                        website.ping_stats_list[3600], 60)
        print_index = self.print_detailed_website_stats(self.window, print_index + 1,
                                                        website.ping_stats_list[600], 10)

        self.window2 = curses.newwin(50, 50, 0, 51)
        self.window2.addstr(0, 0, "Alerts", curses.A_BOLD)
        for i, alert in enumerate(website.alert_history):
            self.window2.addstr(i + 1, 0, f"{alert.message}")

        self.window2.refresh()

        self.window.getch()
        self.screen.clear()
        self.screen.refresh()

    def print_detailed_website_stats(self, window, print_index, stats, timeframe_in_minutes):
        window.addstr(print_index, 0, f"{timeframe_in_minutes} minutes stats", curses.A_BOLD)
        window.addstr(print_index + 1, 0, "Availability: {:.0f}%".format(stats.availability / 100))
        window.addstr(print_index + 2, 0, f"Resp.Time (min/avg/max) in ms: {stats.min_response_time:.0f}/{stats.average_response_time:.0f}/{stats.max_response_time:.0f}")
        window.addstr(print_index + 3, 0, "Response Code count:")
        print_index += 4
        for key in stats.response_codes_dict:
            window.addstr(print_index, 0, f"   {key}: {stats.response_codes_dict[key]}")
            print_index += 1

        return print_index
