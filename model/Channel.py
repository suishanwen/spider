class Channel(object):
    def __init__(self):
        self.spider = ""
        self.pk_org = ""
        self.pk_channel = ""
        self.channel_name = ""
        self.org_name = ""
        self.web_site_url = ""
        self.scrapy_page = ""

    def from_dict(self, _dict):
        for name, value in vars(self).items():
            if name in _dict:
                setattr(self, name, _dict[name])
