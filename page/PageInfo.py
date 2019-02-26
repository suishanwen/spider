class PageInfo(object):
    section = ""
    pk_org = ""
    org_name = ""
    pk_channel = ""
    domain = ""
    name = ""
    url = ""
    web_site_url = ""

    def get_page_count(self, _chrome):
        pass

    def get_sub_page_url(self, page_index):
        pass

    def get_content_list(self, _chrome):
        pass

    def get_content_info(self, _chrome, content):
        pass

    def get_content(self, _chrome):
        pass

    def get_ext_list(self, _chrome):
        pass
