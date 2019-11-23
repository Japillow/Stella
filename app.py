from website import Website


class App(object):
    def __init__(self, websites_conf):
        self.websites = [Website(website_conf[0], int(website_conf[1])) for website_conf in websites_conf]

    def start(self):
        self.check_websites()

    def check_websites(self):

        # only one website for now
        website = self.websites[0]

        for i in range(12):
            website.ping()
            website.contact()
