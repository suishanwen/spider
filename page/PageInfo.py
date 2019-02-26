class PageInfo(object):
    section = ""
    org = ""
    domain = ""
    name = ""
    url = ""

    def get_page_count(self, _chrome):
        pass

    def get_sub_page_url(self, _chrome, page_index):
        pass

    def get_content_list(self, _chrome):
        pass

    def get_content_info(self, _chrome, content):
        pass

    def get_content(self, _chrome):
        pass

    def get_ext_list(self, _chrome):
        pass
