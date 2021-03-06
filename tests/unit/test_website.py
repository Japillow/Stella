import mock
import pytest

from stella import config
from stella.website import Website

TIMEFRAME_FOR_ALERTS = config.ALERTING_TIMEFRAME
SERVER_DOWNTIME = 3 * TIMEFRAME_FOR_ALERTS
DEFAULT_ALERT_THRESHOLD = 0.8


@pytest.fixture
def return_ping_mock():
    return PingMock()


class PingMock(object):

    def __init__(self, *args):
        self.call_count = 0

    def ping_down_n_then_up(self, n):
        if self.call_count > n:
            return (True, 10000, 111)
        else:
            self.call_count += 1
            return (False, None, 999)

    def ping_down_then_up(self, *args, **kwargs):
        return self.ping_down_n_then_up(SERVER_DOWNTIME)


class HttpMock(object):
    def __init__(self, *args):
        self.call_count = 0

    def http_down_n_then_up(self, n):
        if self.call_count > n:
            return (True, 10000, 111)
        else:
            self.call_count += 1
            return (False, None, None)

    def http_down_then_up(self, *args, **kwargs):
        return self.http_down_n_then_up(SERVER_DOWNTIME)


@pytest.mark.parametrize("use_http", [True, False])
class TestAlerting(object):
    @mock.patch('stella.website.Website.http_ping')
    @mock.patch('stella.website.Website.ping')
    def test_alerting_wait_for_enough_data(self, mock_ping, mock_http, use_http):
        """Website is always down since the beginning.

        An alert should only be sent when enough data has been gathered.
        """
        ping_mock = PingMock()
        http_mock = HttpMock()
        mock_ping.side_effect = ping_mock.ping_down_then_up
        mock_http.side_effect = http_mock.http_down_then_up
        website = Website("fakehost.url", 1)

        for i in range(TIMEFRAME_FOR_ALERTS - 1):
            website.ping_and_update_stats(use_http=use_http)
            website.check_for_alert(use_http=use_http)

        assert (len(website.alert_history) == 0), website.alert_history

    @mock.patch('stella.website.Website.http_ping')
    @mock.patch('stella.website.Website.ping')
    def test_alerting_fire_alert(self, mock_ping, mock_http, use_http):
        """Website is down since TIMEFRAME_FOR_ALERTS.

        An alert should be sent as enough data has been gathered.
        """
        ping_mock = PingMock()
        http_mock = HttpMock()
        mock_ping.side_effect = ping_mock.ping_down_then_up
        mock_http.side_effect = http_mock.http_down_then_up
        website = Website("fakehost.url", 1)

        for i in range(TIMEFRAME_FOR_ALERTS):
            website.ping_and_update_stats(use_http=use_http)
            website.check_for_alert(use_http=use_http)

        assert (len(website.alert_history) == 1), website.alert_history

    @mock.patch('stella.website.Website.http_ping')
    @mock.patch('stella.website.Website.ping')
    def test_alerting_only_one_alert_since_down(self, mock_ping, mock_http, use_http):
        """Website is still down.

        Only one alert should be triggered.
        """
        ping_mock = PingMock()
        http_mock = HttpMock()
        mock_ping.side_effect = ping_mock.ping_down_then_up
        mock_http.side_effect = http_mock.http_down_then_up
        website = Website("fakehost.url", 1)

        for i in range(SERVER_DOWNTIME):
            website.ping_and_update_stats(use_http=use_http)
            website.check_for_alert(use_http=use_http)

        # Only one firing alert
        assert (len(website.alert_history) == 1), website.alert_history

    @mock.patch('stella.website.Website.http_ping')
    @mock.patch('stella.website.Website.ping')
    def test_alerting_wait_before_recovering(self, mock_ping, mock_http, use_http):
        """Website is back up after being down for a long time.

        An recovery alert shouldn't be triggered immediately when the website goes back up.
        """
        ping_mock = PingMock()
        http_mock = HttpMock()
        mock_ping.side_effect = ping_mock.ping_down_then_up
        mock_http.side_effect = http_mock.http_down_then_up
        website = Website("fakehost.url", 1)

        for i in range(SERVER_DOWNTIME + 1):
            website.ping_and_update_stats(use_http=use_http)
            website.check_for_alert(use_http=use_http)

        # Only the firing alert, no recovery alert
        assert (len(website.alert_history) == 1), website.alert_history

    @mock.patch('stella.website.Website.http_ping')
    @mock.patch('stella.website.Website.ping')
    def test_alerting_wait_for_threshold_before_recovering(self, mock_ping, mock_http, use_http):
        """Website has been back up for a while.

        Wait until availability is back up to the threshold to send the alert.
        """
        ping_mock = PingMock()
        http_mock = HttpMock()
        mock_ping.side_effect = ping_mock.ping_down_then_up
        mock_http.side_effect = http_mock.http_down_then_up
        website = Website("fakehost.url", 1)

        for i in range(SERVER_DOWNTIME + 2):
            website.ping_and_update_stats(use_http=use_http)
            website.check_for_alert(use_http=use_http)

        assert (len(website.alert_history) == 1), website.alert_history

    @mock.patch('stella.website.Website.http_ping')
    @mock.patch('stella.website.Website.ping')
    def test_alerting_should_have_recovered(self, mock_ping, mock_http, use_http):
        """Website has been back up for a while.

        Wait until availability is back up to the threshold to send the alert.
        """
        ping_mock = PingMock()
        http_mock = HttpMock()
        mock_ping.side_effect = ping_mock.ping_down_then_up
        mock_http.side_effect = http_mock.http_down_then_up
        website = Website("fakehost.url", 1)

        for i in range(SERVER_DOWNTIME + int(0.8 * TIMEFRAME_FOR_ALERTS)):
            website.ping_and_update_stats(use_http=use_http)
            website.check_for_alert(use_http=use_http)
        assert (len(website.alert_history) == 1), website.alert_history

        website.ping_and_update_stats(use_http=use_http)
        website.check_for_alert(use_http=use_http)
        assert (len(website.alert_history) == 2), website.alert_history
