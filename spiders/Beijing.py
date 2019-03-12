from spiders.Spider import Spider


class Beijing(Spider):

    def __init__(self):
        Spider.__init__(self)

    def get_page_count(self, _chrome):
        return int(_chrome.find_class("laypage_last").get_attribute('data-spiders'))

    def get_sub_page_url(self, page_index, page_url):
        return "%s#!spiders=%d" % (page_url, page_index)

    def get_content_list(self, _chrome):
        return _chrome.find_class("zxgklist").find_elements_by_tag_name("li")

    def get_content_info(self, _chrome, content):
        a = content.find_element_by_tag_name("a")
        public_date = content.find_class("date").text
        title = str(a.get_attribute("title"))
        href = a.get_attribute("href")
        return title, href, public_date

    def get_content(self, _chrome):
        return _chrome.find_class("content_con").get_attribute('innerHTML')

    def get_ext_list(self, _chrome):
        return _chrome.chrome.find_element_by_class_name("fujian").find_elements_by_tag_name("a")
