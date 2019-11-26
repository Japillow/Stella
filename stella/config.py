second = 1
minute = 60
hour = 60 * minute

WEBSITES_FILE = "websites.conf"

MONITOR_HTTP_RATHER_THAN_ICMP = True

# # Used for README.md screenshots
# # Stats
# STATS_TIMEFRAMES = [30 * second, 2 * minute, 5 * minute, 10 * minute]

# # Alerting
# DEFAULT_ALERT_THRESHOLD = 0.8
# ALERTING_TIMEFRAME = 5 * second

# Suggested values
# Stats
STATS_TIMEFRAMES = [10 * minute, 1 * hour]

# Alerting
DEFAULT_ALERT_THRESHOLD = 0.8
ALERTING_TIMEFRAME = 2 * minute
