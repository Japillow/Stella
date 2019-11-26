import mock


def test_alerting():
    class PingMock(object):

        def __init__(self, *args):
            self.call_count = 0

        def ping(self, *args, **kwargs):
            if self.call_count > 100:
                return (True, 100, 99)
            else:
                self.call_count += 1
                return (False, None, 999)

    ping_mock = PingMock()
    with mock.patch('stella.helpers.ping', side_effect=ping_mock.ping):
        from stella.website import Website
        website = Website("fakehost.url", 1)
        for i in range(120):
            website.ping_and_update_ping_stats()
            website.check_for_alert()
        assert (len(website.alert_history) == 1), website.alert_history
        for j in range(77):
            website.ping_and_update_ping_stats()
            website.check_for_alert()
        assert (len(website.alert_history) == 1), website.alert_history

        website.ping_and_update_ping_stats()
        website.check_for_alert()
        assert (len(website.alert_history) == 2), website.alert_history
