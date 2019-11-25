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
        self.window = curses.newwin(100, 100, 0, 1)
        self.go_to_home_screen()

    def go_to_home_screen(self):
        _continue = True
        while _continue:
            self.print_home_screen()
            _continue = self.listen_for_input()
        self.exit_dashboard()

    def exit_dashboard(self, _, __):
        self.screen.keypad(False)
        curses.curs_set(True)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        sys.exit(0)

    def print_home_screen(self):
        """Prints the main dashboard screen with the list of all websites and of all alerts."""

        # Print header
        self.window = curses.newwin(2, 100, 0, 1)
        self.window.addstr(0, 0, "Select a website to display additional information:")
        self.window.addstr(1, 0, "(press h for help)")
        self.window.refresh()

        # Initialise columns
        title_lines = 2
        self.window_hostname = curses.newwin(100, 30, title_lines, 1)
        self.window_availability = curses.newwin(100, 20, title_lines, 20)
        self.window_response_time = curses.newwin(100, 20, title_lines, 33)

        self.window_hostname.addstr(0, 0, "Hostname", curses.A_BOLD)
        self.window_availability.addstr(0, 0, " Availability", curses.A_BOLD)
        self.window_response_time.addstr(0, 0, " Resp.Time in ms", curses.A_BOLD)
        self.window_response_time.addstr(1, 0, " (min/avg/max)", curses.A_BOLD)

        # Print columns
        header_lines = 2
        for i, website in enumerate(self.websites):
            if i == self.selected_website:
                self.window_hostname.addstr(i + header_lines, 0, f"> {website.hostname}",
                                            curses.color_pair(1) | curses.A_BOLD)
                self.window_availability.addstr(
                    i + header_lines, 0, f" {website.ping_stats_list[120].availability:.2f}",
                    curses.color_pair(1) | curses.A_BOLD)
                self.window_response_time.addstr(
                    i + header_lines, 0,
                    (f" {website.ping_stats_list[120].min_response_time:.0f}"
                     f"/{website.ping_stats_list[120].average_response_time:.0f}"
                     f"/{website.ping_stats_list[120].max_response_time:.0f}"),
                    curses.color_pair(1) | curses.A_BOLD)

            else:
                self.window_hostname.addstr(i + header_lines, 0, f"  {website.hostname}")
                self.window_availability.addstr(
                    i + header_lines, 0, f" {website.ping_stats_list[120].availability:.2f}")
                self.window_response_time.addstr(
                    i + header_lines, 0,
                    (f" {website.ping_stats_list[120].min_response_time:.0f}"
                     f"/{website.ping_stats_list[120].average_response_time:.0f}"
                     f"/{website.ping_stats_list[120].max_response_time:.0f}"))

        # Print Alerts
        self.window_alerts = curses.newwin(50, 100, 0, 55)
        self.window_alerts.addstr(0, 0, "Alerts", curses.A_BOLD)
        for i, alert in enumerate(self.alert_history):
            self.window_alerts.addstr(i + 1, 0, f"{alert.message}")

        # Show modifications
        self.window_alerts.refresh()
        self.window_hostname.refresh()
        self.window_availability.refresh()
        self.window_response_time.refresh()
        self.window_alerts.refresh()

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
            self.screen.addstr(0, 0, 'An unexpected error occured: ')
            self.screen.addstr(1, 5, f'{exc}')
            self.screen.refresh()
            self.screen.getch()
            self.screen.clear()
            self.screen.refresh()
        return True

    def print_help_screen(self):
        """Prints a help screen"""
        window = curses.newwin(9, 50, 0, 1)
        window.addstr(0, 0, "Help information:")
        window.addstr(2, 0, "  H - This help screen")
        window.addstr(3, 0, "  Q or ESC - Quit the program")
        window.addstr(4, 0, "  Down - Move selection down")
        window.addstr(5, 0, "  Up - Move selection up")
        window.addstr(6, 0, "  Right or Enter - Select website to check")
        window.addstr(8, 0, "Press any key to continue")

        # Wait for any key press to exit page
        window.getch()
        self.screen.clear()
        self.screen.refresh()

    def print_website_page(self, website):
        """Prints a screen detailing all the website information"""
        window = curses.newwin(50, 50, 0, 1)
        website.lock.acquire()
        window.addstr(0, 0, f"Website : {website.hostname}", curses.A_BOLD)
        print_index = self.print_detailed_website_stats(window, 1,
                                                        website.ping_stats_list[3600], 60)
        print_index = self.print_detailed_website_stats(window, print_index + 1,
                                                        website.ping_stats_list[600], 10)
        website.lock.release()

        window_alerts = curses.newwin(50, 100, 0, 51)
        window_alerts.addstr(0, 0, "Alerts", curses.A_BOLD)
        website.lock.acquire()
        for i, alert in enumerate(website.alert_history):
            window_alerts.addstr(i + 1, 0, f"{alert.message}")
        website.lock.release()

        window_alerts.refresh()

        # Wait for any key press to exit page
        window.getch()
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
