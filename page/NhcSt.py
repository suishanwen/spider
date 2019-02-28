from page.PageInfo import PageInfo


class NhcSt(PageInfo):
    section = "nhcSt"

    def get_page_count(self, _chrome):
        text = _chrome.find_class("pagination_index_last").text
        page_count = int(text[text.find("共") + 2:text.find("页") - 1])
        return page_count

    def get_sub_page_url(self, page_index):
        return self.url.replace("ejlist.shtml", "ejlist_%d.shtml" % page_index)

    def get_content_list(self, _chrome):
        return _chrome.find_class("zwgklist").find_elements_by_tag_name("li")

    def get_content_info(self, _chrome, content):
        a = content.find_element_by_tag_name("a")
        public_date = content.find_element_by_tag_name("div").text
        title = str(public_date + "_" + a.get_attribute("title"))
        href = a.get_attribute("href")
        return title, href, public_date

    def check_content_not_exist(self, _chrome):
        return _chrome.page_source().find('<h1>Not Found</h1>') != -1

    def get_content(self, _chrome):
        if _chrome.page_source().find("年鉴") != -1:
            return _chrome.multi_find_class(["mb50", "WordSection1"]).get_attribute('innerHTML')
        return _chrome.multi_find_class(["mb50", "content", "w1100"]).get_attribute('innerHTML')

    def get_ext_list(self, _chrome):
        if _chrome.page_source().find("年鉴") != -1:
            return _chrome.chrome.find_elements_by_class_name("t0i").find_elements_by_tag_name("a")
        return _chrome.chrome.find_element_by_class_name("con").find_elements_by_tag_name("a")
