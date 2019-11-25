# Stella

## About

Stella is a console program which monitors availability and performance of websites

## Setup

### Requirements

- Linux, MacOS or Windows.
- Python 3.7

This program uses the included _curses_ library. As the regular Windows Python distribution does not include the _curses_ library  used for the console dashboard, the _windows-curses_ library is required.

### Installation and running

To install from source in a virtualenv:

- python setup.py install
- Run `stella`

If you do not want to install the program, you can also call it by using `python main.py`

## Configuration

Modify the websites you would like to monitor in the `websites.conf` file.
Each line represents a website and check interval, separated by a space.

## Architecture

The architecture is divided into 3 main components:

- The App, which acts as the controller
- The Dashboard, which presents information to the user
- The Website, which contains several Stats objects

the App runs a monitoring thread per website, which updates website stats, and eventually creates an Alert.

## Improvements

### Features

- Add more stats, such as the 95th or 99th percentile of response times, which provide a better insight into the health of the website than the average.
- Better display the alert codes based on their signification.
- Alerting configuration : the check_for_alert is hardcoded for the availability of the 2 minutes. Add an alert config file indicating the metric, threshold and time_frame to monitor.

### Implementation

- Stats objects are built based on the assumption that stats will be updated every check_interval. If for some reason the stats are not updated (for exemple if monitoring is paused), the stats do not really represent the last time timeframe of data. Therefore, add the notion of timestamp for each new data, and compute stats based on the timestamps.
- Errors in parsing the `websites.conf` conf files are not handled : improve parsing (check integer and url integrity)  to help the user identify when there is an error in the config file.
- Website monitoring cannot be stopped (infinite loops) : add a stop condition at each monitoring loop (along with simple start/stop helper functions.
- The alert_history is shared among all websites : replace the alert_history in the app.monitoring_website function by a producer/consumer queue per website, whereby each websites produces alerts and the main thread consumes them.
- The helper.ping subprocess.run call (to the system ICMP ping) blocks the thread, therefore the program. This therefore currently represents the main bottleneck.
- Website monitoring is done with one thread per website. Due to the python Global Interpreter Lock, they do not run concurrently, allowing potential bottlenecks for the program. For example, if connection is poor and ICMP ping takes more than 1 second, no more than one website will be able to update its stats.
