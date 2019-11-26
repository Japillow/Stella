import curses
import curses.ascii
from signal import alarm, signal, SIGALRM, SIGINT, SIGTERM
import sys


class Dashboard(object):
    """Object responsible for initialising and updating the console output using curses.

    Note
    ----
    Console update is based on :
    - user input
    - automatic reload every 10 seconds on Linux and Mac (using SIGALRM).
    """
    def __init__(self, screen, websites, alert_history):
        """Initialises a curses console.

        Parameters
        ----------
        screen : _CursesWindow
            main console screen, on which to build windows, and from which to retrieve user input
        websites : list
            list of Website objects containing their stats
        """

        signal(SIGINT, self.exit_dashboard)
        signal(SIGTERM, self.exit_dashboard)
        self.screen = screen
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.curs_set(False)
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
        self.screen.keypad(True)
        self.websites = websites
        self.selected_website = 0
        self.alert_history = alert_history
        self.refresh_interval = 10

    def start(self):
        self.screen.clear()
        self.screen.refresh()
        self.go_to_home_screen()

    def go_to_home_screen(self):
        _continue = True
        while _continue:
            self.print_home_screen()
            _continue = self.listen_for_input()
        self.exit_dashboard(None, None)

    def exit_dashboard(self, _, __):
        self.screen.keypad(False)
        curses.curs_set(True)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        sys.exit(0)

    def newwin(height, width, start_y=0, start_x=0, title=None, borders=True):
        window = curses.newwin(height, width, start_y, start_x)
        if borders:
            window.border()
        if title is not None:
            window.addstr(0, max(1, (width - len(title)) // 2), title, curses.A_BOLD)
        return window

    def print_home_screen(self):
        """Prints the main dashboard screen with the list of all websites and of all alerts."""

        # Print header
        self.window = Dashboard.newwin(0, 52, 0, 0,
                                       "Select a website to display additional information:", False)
        self.window.addstr(1, 1, "(press h for help)")
        self.window.refresh()

        ws_nb = len(self.websites)
        # Initialise columns
        self.window_hostname = Dashboard.newwin(ws_nb + 4, 25, 2, 0, "Hostname")
        self.window_availability = Dashboard.newwin(ws_nb + 4, 15, 2, 24, "Availability")
        self.window_response_time = Dashboard.newwin(ws_nb + 4, 18, 2, 24 + 13, "Resp.Time in ms")
        self.window_alerts = Dashboard.newwin(10, 55, ws_nb + 6, 0, "Alerts")

        self.window_response_time.addstr(1, 1, " (min/avg/max)", curses.A_BOLD)

        # Print columns
        header_lines = 2
        for i, website in enumerate(self.websites):
            website.lock.acquire()
            if i == self.selected_website:
                self.window_hostname.addstr(i + header_lines, 1, f"> {website.hostname}",
                                            curses.color_pair(1) | curses.A_BOLD)
                self.window_availability.addstr(
                    i + header_lines, 3, f"{website.ping_stats_list[120].availability:.2f}",
                    curses.color_pair(1) | curses.A_BOLD)
                self.window_response_time.addstr(
                    i + header_lines, 3,
                    (f"{website.ping_stats_list[120].min_response_time:.0f}"
                     f"/{website.ping_stats_list[120].average_response_time:.0f}"
                     f"/{website.ping_stats_list[120].max_response_time:.0f}"),
                    curses.color_pair(1) | curses.A_BOLD)

            else:
                self.window_hostname.addstr(i + header_lines, 1, f"  {website.hostname}")
                self.window_availability.addstr(
                    i + header_lines, 3, f"{website.ping_stats_list[120].availability:.2f}")
                self.window_response_time.addstr(
                    i + header_lines, 3,
                    (f"{website.ping_stats_list[120].min_response_time:.0f}"
                     f"/{website.ping_stats_list[120].average_response_time:.0f}"
                     f"/{website.ping_stats_list[120].max_response_time:.0f}"))
            website.lock.release()

        # Print Alerts
        for i, alert in enumerate(self.alert_history):
            self.window_alerts.addstr(i + 1, 1, f"{alert.message}")

        # Show modifications
        self.window_hostname.noutrefresh()
        self.window_availability.noutrefresh()
        self.window_response_time.noutrefresh()
        self.window_alerts.noutrefresh()
        curses.doupdate()

    def listen_for_input(self):
        """Listen for input on the main screen and take action.

        Either refresh the main screen, print the requested screen or quit the dashboard.
        """
        try:
            # Listen for user input for self.refresh_interval
            # if no signal recieved, go back to home screen (i.e. refresh)
            signal(SIGALRM, self.go_to_home_screen)
            alarm(self.refresh_interval)
            char_ord = self.screen.getch()
            alarm(0)
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
            self.screen.addstr(0, 1, 'An unexpected error occured: ')
            self.screen.addstr(1, 5, f'{exc}')
            self.screen.refresh()
            self.screen.getch()
            self.screen.clear()
            self.screen.refresh()
        return True

    def print_help_screen(self):
        """Prints a help screen"""
        window = Dashboard.newwin(9, 45, 0, 0, "Help information:")
        window.addstr(1, 1, "H - This help screen")
        window.addstr(2, 1, "Q or ESC - Quit the program")
        window.addstr(3, 1, "Down - Move selection down")
        window.addstr(4, 1, "Up - Move selection up")
        window.addstr(5, 1, "Right or Enter - Select website to check")
        window.addstr(7, 1, "Press any key to continue")

        # Wait for any key press to exit page
        window.getch()
        self.screen.clear()
        self.screen.refresh()

    def print_website_page(self, website):
        """Prints a screen detailing all the website information"""
        window = Dashboard.newwin(50, 50, 0, 1)
        website.lock.acquire()
        window.addstr(0, 1, f"Website : {website.hostname}", curses.A_BOLD)
        print_index = self.print_detailed_website_stats(window, 1,
                                                        website.ping_stats_list[3600], 60)
        print_index = self.print_detailed_website_stats(window, print_index + 1,
                                                        website.ping_stats_list[600], 10)
        website.lock.release()

        window_alerts = Dashboard.newwin(50, 50, 0, 51, "Alerts")
        website.lock.acquire()
        for i, alert in enumerate(website.alert_history):
            window_alerts.addstr(2*i + 1, 1, f"{alert.message}")
        website.lock.release()

        window_alerts.refresh()

        # Wait for any key press to exit page
        window.getch()
        self.screen.clear()
        self.screen.refresh()

    def print_detailed_website_stats(self, window, print_index, stats, timeframe_in_minutes):
        window.addstr(print_index, 2, f"{timeframe_in_minutes} minutes stats", curses.A_BOLD)
        window.addstr(print_index + 1, 2, "Availability: {:.0f}%".format(stats.availability / 100))
        window.addstr(print_index + 2, 2, f"Resp.Time (min/avg/max) in ms: {stats.min_response_time:.0f}/{stats.average_response_time:.0f}/{stats.max_response_time:.0f}")
        window.addstr(print_index + 3, 2, "Response Code count:")
        print_index += 4
        for key in stats.response_codes_dict:
            window.addstr(print_index, 3, f"{key}: {stats.response_codes_dict[key]}")
            print_index += 1

        return print_index
