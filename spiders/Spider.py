class Spider(object):
    def __init__(self):
        self.max_thread = 1
        self.breakpoint_download = True
        self.channels = []

    def get_page_count(self, _chrome):
        pass

    def get_sub_page_url(self, page_index, page_url):
        pass

    def get_content_list(self, _chrome):
        pass

    def get_content_info(self, _chrome, content):
        pass

    def check_content_status(self, _chrome):
        content = _chrome.page_source()
        code = 200
        if content.find('<h1>Not Found</h1>') != -1:
            code = 404
        elif content.find('<h1>Forbidden</h1>') != -1:
            code = 403
        elif content.find('503 Service Unavailable') != -1:
            code = 503
        return code

    def get_content(self, _chrome):
        pass

    def get_ext_list(self, _chrome):
        pass

    def replace_ext_url(self, content, attachment):
        return content
