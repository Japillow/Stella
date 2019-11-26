from collections import deque


class Stats(object):
    """Class used to store metrics along with related stats."""

    def __init__(self, check_interval, compute_timeframe):
        """Returns an instance of Stats.

        Parameters
        ----------
        check_interval : int
            in seconds, the frequency at which the stats are updated
        compute_timeframe : int
            in seconds, the duration upon which the stats are computed

        Attributes
        ----------
        max_nb_data_points : int
            number of data points to be recieved in the given computed timeframe
        successes_in_timeframe : int
            number of successful availability checks recieved in the last timeframe.
            used to compute the availability.
        sum_response_times : float
            sum of the response times recieved in the last timeframe.
        ups : deque(int)
            Queue with the result of the availability checks (0 or 1) recieved in the last timeframe.
            Used to determine if there is a response time and response code associated with the check.
        response_times : deque(float)
            Queue with the response time recieved in the last timeframe.
            If no response time is provided during the update, no element is added.
        response_codes : deque(int)
            Queue with the response code recieved in the last timeframe
            If no response code is provided during the update, no element is added.
        availability : float
            portion of successful availability checks.
            Used to access the mean value of ups in constant time.
        max_response_time : float
            Used to access the maximum value of responses in response_times in constant time.
        min_response_time : float
            Used to access the minimum value of responses in response_times in constant time.
        average_response_time :
            Used to access the mean value of responses in response_times in constant time.
        response_codes_dict : dict(int:int)
            Map of the amount of each response code recieved in the last timeframe.
            Used to access the response codes in constant time.
        """

        if not (float(compute_timeframe) / check_interval).is_integer():
            raise ValueError(
                f"Check interval ({check_interval}) must be a divider of {compute_timeframe}")
        else:
            self.max_nb_data_points = compute_timeframe // check_interval

        self.successes_in_timeframe = 0
        self.sum_response_times = 0

        self.ups = deque()
        self.response_times = deque()
        self.response_codes = deque()

        self.availability = 0
        self.max_response_time = -float('inf')
        self.min_response_time = float('inf')
        self.average_response_time = float('inf')
        self.response_codes_dict = {}

    def update(self, is_up, response_time=None, response_code=None, always_a_response_code=False):
        """Updates the stats object with data from a new check.

        Adds the success status, response time and response time to memory,
        removes old values (those older than the compute timeframe), and
        updates the stats in constant time most of the time
        (apart when max or min is removed. [...])

        """

        # Remove old availability status
        if len(self.ups) == self.max_nb_data_points:
            was_up_timeframe_ago = self.ups.popleft()
        else:
            was_up_timeframe_ago = 0

        # Add new availability status
        self.ups.append(is_up)
        self.successes_in_timeframe += is_up - was_up_timeframe_ago

        if was_up_timeframe_ago:
            # Remove old response time
            old_response_time = self.response_times.popleft()
            self.sum_response_times -= old_response_time
            # Update response time stats
            if old_response_time == self.max_response_time:
                if len(self.response_times) == 0:
                    self.max_response_time = -float('inf')
                else:
                    self.max_response_time = max(self.response_times)
            if old_response_time == self.min_response_time:
                if len(self.response_times) == 0:
                    self.min_response_time = float('inf')
                else:
                    self.min_response_time = min(self.response_times)

        if was_up_timeframe_ago or (always_a_response_code and len(self.response_codes) == self.max_nb_data_points):
            # Remove old response code
            old_response_code = self.response_codes.popleft()
            # Update response code stats
            self.response_codes_dict[old_response_code] -= 1

        if is_up:
            # Add new response time
            self.sum_response_times += response_time
            self.response_times.append(response_time)
            # Update response time stats
            self.max_response_time = max(self.max_response_time, response_time)
            self.min_response_time = min(self.min_response_time, response_time)

        if is_up or always_a_response_code:
            # Add new response code
            self.response_codes.append(response_code)
            # Update response code stats
            if response_code in self.response_codes_dict:
                self.response_codes_dict[response_code] += 1
            else:
                self.response_codes_dict[response_code] = 1

        # Update remaining stats
        self.availability = self.successes_in_timeframe / self.nb_data_points()
        if self.successes_in_timeframe > 0:
            self.average_response_time = self.sum_response_times / self.successes_in_timeframe

    def nb_data_points(self):
        """Returns the number of data points recieved yet.

        Slowly increases up to self.max_nb_data_points.
        """
        return len(self.ups)

    def timeframe_reached(self):
        """Return whether we have already reached the max number of data points."""
        return self.nb_data_points() == self.max_nb_data_points


class HttpStats(Stats):
    """Use to store stats for HTTP pings.

    Ensures both response times and response codes are provided if the website is online
    """
    def update(self, is_up, response_time=None, response_code=None):
        if is_up and (response_time is None or response_time is None):
            raise ValueError("Site is available but no additional information given")
        super().update(is_up, response_time, response_code)


class PingStats(Stats):
    """Use to store stats for ICMP pings.

    Ensures a response code is provided, and
    ensures a response time is provided if the website is online.
    """
    def update(self, is_up, response_time=None, response_code=None):
        if response_code is None:
            raise ValueError("Ping should return a response code")
        if is_up and response_time is None:
            raise ValueError("Successful ping should return a response time")
        super().update(is_up, response_time, response_code, always_a_response_code=True)
