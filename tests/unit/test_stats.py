import random

from stella.stats import Stats, HttpStats, PingStats


def test_stats_length():
    stats = Stats(1, 10)
    for i in range(15):
        is_up = random.randint(0, 1)
        response_time = None
        response_code = None
        if is_up:
            response_time = random.randint(0, 10000)
            response_code = random.randint(0, 70)
        stats.update(is_up, response_time, response_code)
        assert len(stats.ups) <= stats.max_nb_data_points
        assert len(stats.response_times) == stats.successes_in_timeframe


def test_ping_stats_length():
    stats = PingStats(1, 10)
    for i in range(15):
        is_up = random.randint(0, 1)
        response_time = None
        response_code = random.randint(0, 70)
        if is_up:
            response_time = random.randint(0, 10000)
        stats.update(is_up, response_time, response_code)

        assert len(stats.response_codes) == len(stats.ups), (len(stats.response_codes), len(stats.ups))


def test_http_stats_length():
    stats = HttpStats(1, 10)
    for i in range(15):
        is_up = random.randint(0, 1)
        response_time = None
        response_code = random.randint(0, 70)
        if is_up:
            response_time = random.randint(0, 10000)
        stats.update(is_up, response_time, response_code)

        assert len(stats.response_codes) == stats.successes_in_timeframe
