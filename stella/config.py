second = 1
minute = 60
hour = 60 * minute

WEBSITES_FILE = "websites.conf"

# Stats
STATS_TIMEFRAMES = [2 * minute, 10 * minute, 1 * hour]
DISPLAY_INTERVALS = [(10 * second, 10 * minute),
                     (1 * minute, 1 * hour)]

# Alerting
DEFAULT_ALERT_THRESHOLD = 0.8
