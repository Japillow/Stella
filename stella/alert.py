import datetime


class Alert(object):
    def __init__(self, website, availability):
        self.website = website
        self.availability = availability
        self.activation_time = datetime.datetime.now()
        # self.str_activation_time = self.activation_time.strftime("%d/%m/%y %H:%M:%S")
        self.message = None


class AvailabilityAlert(Alert):
    def __init__(self, website, availability):
        super().__init__(website, availability)
        self.message = f"Website {website} is down. availability={availability:0.3f}, time={self.activation_time}"


class AvailabilityRecovered(Alert):
    def __init__(self, website, availability):
        super().__init__(website, availability)
        self.message = f"Website {website} is back up. availability={availability:0.3f}, time={self.activation_time}"
