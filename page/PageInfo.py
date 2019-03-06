class PageInfo(object):
    def __init__(self):
        # child init
        self.section = ""
        # from yaml
        self.org_name = ""
        self.domain = ""
        self.channel = ""
        self.pages = []
        self.max_thread = 1
        # query
        self.pk_org = ""
        self.pk_channel = ""
        # for update
        self.known_hosts = []

    def from_dict(self, _dict):
        for name, value in vars(self).items():
            if name in _dict:
                setattr(self, name, _dict[name])

    def append_host(self, url):
        self.known_hosts.append(url)

    def contains_host(self, url):
        for host in self.known_hosts:
            if host in url:
                return True
        return False

    def set_pk_org(self, pk_org):
        self.pk_org = pk_org

    def set_pk_channel(self, pk_channel):
        self.pk_channel = pk_channel

    def get_page_count(self, _chrome):
        pass

    def get_sub_page_url(self, page_index, page_url):
        pass

    def get_content_list(self, _chrome):
        pass

    def get_content_info(self, _chrome, content):
        pass

    def check_content_not_exist(self, _chrome):
        pass

    def get_content(self, _chrome):
        pass

    def get_ext_list(self, _chrome):
        pass
