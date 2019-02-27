class PageInfo(object):
    section = ""
    pk_org = ""
    org_name = ""
    pk_channel = ""
    domain = ""
    web_site_url = ""
    pages = ""
    index = 0
    name = ""
    url = ""
    page_exec = 0

    def get_page_count(self, _chrome):
        pass

    def get_sub_page_url(self, page_index):
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
