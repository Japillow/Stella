from collections import deque
# import time


class Stats(object):
    def __init__(self, check_interval, compute_timeframe):
        """Returns an instance of Stats.

        check_interval and compute_timeframe are both in seconds.
        """

        if not (float(compute_timeframe) / check_interval).is_integer():
            raise ValueError(
                f"Check interval ({check_interval}) must be a divider of {compute_timeframe}")
        else:
            self.data_points = compute_timeframe // check_interval

        self.successes_in_timeframe = 0
        self.sum_response_times = 0

        self.ups = deque()
        self.response_times = deque()
        self.response_codes = deque()
        self.response_codes_dict = {} # To access response codes in constant time

        self.availability = None
        self.max_response_time = 0.
        self.min_response_time = float('inf')
        self.average_response_time = float('inf')

    def update(self, is_up, response_time=None, response_code=None, always_a_response_code=False):

        # start = time.time()

        if len(self.ups) == self.data_points:
            was_up_timeframe_ago = self.ups.popleft()
        else:
            was_up_timeframe_ago = 0

        if was_up_timeframe_ago:
            # remove old response time
            old_response_time = self.response_times.popleft()
            self.sum_response_times -= old_response_time
            if old_response_time == self.max_response_time:
                self.max_response_time = max(self.response_times)
            if old_response_time == self.min_response_time:
                self.min_response_time = min(self.response_times)

        if was_up_timeframe_ago or (always_a_response_code and len(self.ups) == self.data_points):
            # remove old response code
            old_response_code = self.response_codes.popleft()
            self.response_codes_dict[old_response_code] -= 1

        self.ups.append(is_up)
        self.successes_in_timeframe += is_up - was_up_timeframe_ago

        if is_up:
            # add new response time
            self.sum_response_times += response_time
            self.response_times.append(response_time)
            self.max_response_time = max(self.max_response_time, response_time)
            self.min_response_time = min(self.min_response_time, response_time)

        if is_up or always_a_response_code:
            # add new response code
            self.response_codes.append(response_code)
            if response_code in self.response_codes_dict:
                self.response_codes_dict[response_code] += 1
            else:
                self.response_codes_dict[response_code] = 1

        self.availability = self.successes_in_timeframe / self.data_points
        if self.successes_in_timeframe > 0:
            self.average_response_time = self.sum_response_times / self.successes_in_timeframe

        assert len(self.ups) <= self.data_points
        assert len(self.response_times) == self.successes_in_timeframe


class HttpStats(Stats):
    def update(self, is_up, response_time=None, response_code=None):
        if is_up and (response_time is None or response_time is None):
            raise ValueError("Site is available but no additional information given")
        super().update(is_up, response_time, response_code)
        assert len(self.response_codes) == self.successes_in_timeframe


class PingStats(Stats):
    def update(self, is_up, response_time=None, response_code=None):
        if response_code is None:
            raise ValueError("Ping should return a response code")
        super().update(is_up, response_time, response_code, always_a_response_code=True)
        assert len(self.response_codes) == len(self.ups)
