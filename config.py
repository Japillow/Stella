from datetime import timedelta

WEBSITES_FILE = "websites.conf"

# Stats
STATS_TIMEFRAME = [timedelta(minutes=2), timedelta(minutes=10)]
DISPLAY_INTERVALS = [(timedelta(seconds=10), timedelta(minutes=10)),
                     (timedelta(minutes=1), timedelta(hours=1))]
