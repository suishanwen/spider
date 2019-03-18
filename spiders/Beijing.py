from spiders.Spider import Spider
from selenium.common.exceptions import NoSuchElementException


class Beijing(Spider):

    def __init__(self):
        Spider.__init__(self)
        self.breakpoint_download = False

    def check_content_status(self, _chrome):
        content = _chrome.page_source()
        code = 200
        if content.find('http://www.beijing.gov.cn/images/404_mzq_20160906.png') != -1:
            code = 404
        elif content.find('<h1>Forbidden</h1>') != -1:
            code = 403
        elif content.find('503 Service Unavailable') != -1:
            code = 503
        elif content.find('最近有可疑的攻击行为，请稍后重试') != -1:
            code = 999
        return code

    def get_page_count(self, _chrome):
        try:
            text = _chrome.find_class("laypage_last")
            page_count = int(text.get_attribute('data-page'))
        except NoSuchElementException:
            page_count = 1
        return page_count

    def get_sub_page_url(self, page_index, page_url):
        return "%s#!page=%d" % (page_url, page_index)

    def get_content_list(self, _chrome):
        return _chrome.find_class("zxgklist").find_elements_by_tag_name("li")

    def get_content_info(self, _chrome, content):
        a = content.find_element_by_tag_name("a")
        public_date = content.find_element_by_class_name("date").text
        title = str(a.get_attribute("title"))
        href = a.get_attribute("href")
        return title, href, public_date

    def get_content(self, _chrome):
        return _chrome.find_class("content_con").get_attribute('innerHTML')

    def get_ext_list(self, _chrome):
        con_classes = ["fujian", "content"]
        ext_a_list = []
        for _class in con_classes:
            for ext in _chrome.chrome.find_elements_by_class_name(_class):
                ext_a_list += ext.find_elements_by_tag_name("a")
        return ext_a_list
