second = 1
minute = 60
hour = 60 * minute

################################################################
# Suggested values, Used for README.md screenshots

WEBSITES_FILE = "websites.conf"
MONITOR_HTTP_RATHER_THAN_ICMP = False

# Stats
CONSOLE_REFRESH_INTERVAL = 1
STATS_TIMEFRAMES = [30 * second, 2 * minute, 5 * minute, 10 * minute]

# Alerting
DEFAULT_ALERT_THRESHOLD = 0.8
ALERTING_TIMEFRAME = 5 * second

################################################################

# # Uncomment the section below to overide the suggested values
# # Values used for the Datadog Project :

# WEBSITES_FILE = "websites.conf"
# CONSOLE_REFRESH_INTERVAL = 10
# MONITOR_HTTP_RATHER_THAN_ICMP = True
# STATS_TIMEFRAMES = [2 * minute, 10 * minute, 1 * hour]
# DEFAULT_ALERT_THRESHOLD = 0.8
# ALERTING_TIMEFRAME = 2 * minute
