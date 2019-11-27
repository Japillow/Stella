import curses
import curses.ascii
from signal import alarm, signal, SIGALRM, SIGINT, SIGTERM
import sys

from stella import config


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
            list of Website objects containing their Stats and Alerts
        alert_history : list
            list of Alert to display them
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
        self.refresh_interval = config.CONSOLE_REFRESH_INTERVAL
        self.main_screen_timeframe = config.ALERTING_TIMEFRAME

    def start(self):
        self.screen.clear()
        self.screen.refresh()
        self.go_to_home_screen(None, None)

    def go_to_home_screen(self, _, __):
        """Loops through the home screen, listens for user input and periodically refreshes the interface."""
        self._continue = True
        while self._continue:
            self.print_home_screen()
            self._continue = self.listen_for_input()
        self.exit_dashboard(None, None)

    def exit_dashboard(self, signal_arg1, signal_arg2):
        """Cleans up terminal before exiting"""
        self.screen.keypad(False)
        curses.curs_set(True)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        if signal_arg1 is not None:
            sys.exit(0)  # Force exit when launched with signals
        else:
            pass # Program will exit naturally

    def newwin(height, width, start_y=0, start_x=0, title=None, borders=True):
        """Create a new dashboard window with optional borders and title"""
        window = curses.newwin(height, width, start_y, start_x)
        if borders:
            window.border()
        if title is not None:
            window.addstr(0, max(1, (width - len(title)) // 2), title, curses.A_BOLD)
        return window

    def print_home_screen(self):
        """Prints the main dashboard screen with the list of all websites and of all alerts."""

        # Print header
        monitoring_type = "HTTP" if config.MONITOR_HTTP_RATHER_THAN_ICMP else "Ping"
        self.window = Dashboard.newwin(
            0, 56, 0, 0, f"Welcome to Stella : {monitoring_type} Monitoring (press h for help)",
            False)
        self.window.addstr(1, 1, "Select a website to display additional information:")
        self.window.refresh()

        ws_nb = max(len(self.websites) + 4, len(config.STATS_TIMEFRAMES) * 5)
        # Initialise columns
        self.window_hostname = Dashboard.newwin(ws_nb, 30, 2, 0, "Hostname")
        self.window_availability = Dashboard.newwin(ws_nb, 15, 2, 29, "Availability")
        self.window_response_time = Dashboard.newwin(ws_nb, 18, 2, 29 + 13, "Resp.Time in ms")
        self.window_alerts = Dashboard.newwin(ws_nb + 2, 95, ws_nb + 2, 0,
                                              f"Alerts ({config.ALERTING_TIMEFRAME}s timeframe)")

        self.window_response_time.addstr(1, 1, " (min/avg/max)", curses.A_BOLD)

        # Print columns
        header_lines = 2
        for i, website in enumerate(self.websites):
            website.lock.acquire()
            stats_list = website.http_stats_list if config.MONITOR_HTTP_RATHER_THAN_ICMP else website.ping_stats_list

            if i == self.selected_website:
                self.window_hostname.addstr(i + header_lines, 1, f"> {website.hostname}",
                                            curses.color_pair(1) | curses.A_BOLD)
                self.window_availability.addstr(
                    i + header_lines, 3,
                    f"{stats_list[config.ALERTING_TIMEFRAME].availability:.2f}",
                    curses.color_pair(1) | curses.A_BOLD)
                self.window_response_time.addstr(
                    i + header_lines, 3,
                    (f"{stats_list[config.ALERTING_TIMEFRAME].min_response_time:.0f}"
                     f"/{stats_list[config.ALERTING_TIMEFRAME].average_response_time:.0f}"
                     f"/{stats_list[config.ALERTING_TIMEFRAME].max_response_time:.0f}"),
                    curses.color_pair(1) | curses.A_BOLD)

            else:
                self.window_hostname.addstr(i + header_lines, 1, f"  {website.hostname}")
                self.window_availability.addstr(
                    i + header_lines, 3,
                    f"{stats_list[config.ALERTING_TIMEFRAME].availability:.2f}")
                self.window_response_time.addstr(
                    i + header_lines, 3,
                    (f"{stats_list[config.ALERTING_TIMEFRAME].min_response_time:.0f}"
                     f"/{stats_list[config.ALERTING_TIMEFRAME].average_response_time:.0f}"
                     f"/{stats_list[config.ALERTING_TIMEFRAME].max_response_time:.0f}"))
            website.lock.release()

        # Print Alerts
        self.print_alerts(self.window_alerts, self.alert_history, ws_nb + 2)

        # Detailed information
        self.window_detailed = Dashboard.newwin(ws_nb + 2, 35, 0, 60)
        website = self.websites[self.selected_website]
        website.lock.acquire()
        self.window_detailed.addstr(0, 1, f"Website : {website.hostname}", curses.A_BOLD)
        print_index = 0
        for timeframe in config.STATS_TIMEFRAMES:
            stats_list = website.http_stats_list if config.MONITOR_HTTP_RATHER_THAN_ICMP else website.ping_stats_list
            print_index = self.print_detailed_website_stats(
                self.window_detailed, print_index + 1, stats_list[timeframe],
                timeframe / 60, False)
        website.lock.release()

        # Show modifications
        self.window_hostname.noutrefresh()
        self.window_availability.noutrefresh()
        self.window_response_time.noutrefresh()
        self.window_detailed.noutrefresh()
        curses.doupdate()

    def listen_for_input(self):
        """Listens for user input on the main screen, and takes action accordingly.

        Options include :
        - change selected website
        - print the selected website page
        - Print help window
        - Quit the dashboard.
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
        window = Dashboard.newwin(50, 35, 0, 1)
        website.lock.acquire()
        window.addstr(0, 1, f"Website : {website.hostname}", curses.A_BOLD)
        print_index = 0
        for timeframe in config.STATS_TIMEFRAMES:
            stats_list = website.http_stats_list if config.MONITOR_HTTP_RATHER_THAN_ICMP else website.ping_stats_list
            print_index = self.print_detailed_website_stats(window, print_index + 1,
                                                            stats_list[timeframe], timeframe // 60)
        website.lock.release()

        window_alerts = Dashboard.newwin(50, 95, 0, 35,
                                         f"Alerts ({config.ALERTING_TIMEFRAME}s timeframe)")
        website.lock.acquire()
        self.print_alerts(window_alerts, website.alert_history, 50)
        website.lock.release()

        # Wait for any key press to exit page
        window.getch()
        self.screen.clear()
        self.screen.refresh()

    def print_detailed_website_stats(self, window, print_index, stats, timeframe_in_minutes, print_response_codes=True):
        """Prints some stats attributes.

        Parameters
        ----------
        window : _CursesWindow
            The window in which to print the stats
        print_index : int
            Line in window at which to start printing
        stats : stats.Stats
            a Stats object
        timeframe_in_minutes : float
            used to display information on the stat list
        print_response_codes : bool
            whether to print the response codes
        """
        window.addstr(print_index, 2, f"{timeframe_in_minutes} minutes stats", curses.A_BOLD)
        window.addstr(print_index + 1, 2, "Availability: {:.0f}%".format(stats.availability * 100))
        window.addstr(print_index + 2, 2, "Resp.Time in ms:")
        window.addstr(
            print_index + 3, 2,
            f"min/avg/max: {stats.min_response_time:.0f}/{stats.average_response_time:.0f}/{stats.max_response_time:.0f}"
        )
        print_index += 4
        if print_response_codes:
            window.addstr(print_index, 2, "Response Code count:")
            print_index += 1
            for key in stats.response_codes_dict:
                window.addstr(print_index, 3, f"{key}: {stats.response_codes_dict[key]}")
                print_index += 1

        return print_index

    def print_alerts(self, window, alert_history, window_height):
        """Limit the alert printing to the window_height to prevent curses from crashing."""
        for i, alert in enumerate(alert_history[:window_height - 2]):
            window.addstr(i + 1, 1, f"{alert.message}")
        window.refresh()
