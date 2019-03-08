from page.PageInfo import PageInfo
from util.file import is_appendix_file
import time


class NhcSt(PageInfo):

    def __init__(self):
        PageInfo.__init__(self)
        self.section = "nhcSt"

    def get_page_count(self, _chrome):
        text = _chrome.find_class("pagination_index_last").text
        page_count = int(text[text.find("共") + 2:text.find("页") - 1])
        return page_count

    def get_sub_page_url(self, page_index, page_url):
        return page_url.replace("ejlist.shtml", "ejlist_%d.shtml" % page_index)

    def get_content_list(self, _chrome):
        return _chrome.find_class("zwgklist").find_elements_by_tag_name("li")

    def get_content_info(self, _chrome, content):
        a = content.find_element_by_tag_name("a")
        public_date = content.find_element_by_tag_name("div").text
        title = str(a.get_attribute("title"))
        href = a.get_attribute("href")
        return title, href, public_date

    def check_content_not_exist(self, _chrome):
        return _chrome.page_source().find('<h1>Not Found</h1>') != -1

    def get_content(self, _chrome):
        if _chrome.page_source().find("年鉴") != -1 or _chrome.current_url().find("tjnj") != -1:
            url = _chrome.current_url()
            helper_url = url[0:url.rfind("/") + 1] + "helpcontents.html"
            _chrome.get(helper_url)
            if not self.check_content_not_exist(_chrome):
                return _chrome.page_source()
            else:
                _chrome.get(url)
                time.sleep(1)
        return _chrome.multi_find_class(["mb50", "brcon", "zwcon", "content"]).get_attribute('innerHTML')

    def get_ext_list(self, _chrome):
        if _chrome.current_url().find("helpcontents.html") != -1:
            tables = _chrome.chrome.find_elements_by_tag_name("table")
            a_result = []
            for table in tables:
                a_list = table.find_elements_by_tag_name("a")
                for a in a_list:
                    href = a.get_attribute('href')
                    # 过滤去重
                    if is_appendix_file(href) and len(
                            list(filter(lambda x: True if x.get_attribute('href') == href else False,
                                        a_result))) == 0:
                        a_result.append(a)
            return a_result
        con_classes = ["con", "content"]
        ext_a_list = []
        for _class in con_classes:
            for ext in _chrome.chrome.find_elements_by_class_name(_class):
                ext_a_list += ext.find_elements_by_tag_name("a")
        return ext_a_list
