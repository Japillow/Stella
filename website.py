from urllib.parse import urlparse

from helpers import ping


class Website(object):
    def __init__(self, website_url):
        self.url = website_url
        parsed_url = urlparse(website_url)
        self.hostname = parsed_url.netloc

    def ping(self):
        if ping(self.hostname):
            print(f"{self.hostname} ping successful")
        else:
            print(f"{self.hostname} ping failed")
