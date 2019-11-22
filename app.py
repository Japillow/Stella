from website import Website


class App(object):
    def __init__(self, website_urls):
        self.websites = [Website(url) for url in website_urls]

    def start(self):
        # print([(f"Starting Monitoring for : {website.url}") for website in self.websites])
        self.check_websites()

    def check_websites(self):
        for website in self.websites:
            website.ping()
