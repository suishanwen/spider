from page.PageInfo import PageInfo


class NhcSt(PageInfo):
    section = "nhcSt"

    def get_page_count(self, _chrome):
        text = _chrome.find_element_by_class_name("pagination_index_last").text
        page_count = int(text[text.find("共") + 2:text.find("页") - 1])
        return page_count

    def get_sub_page_url(self, _chrome, page_index):
        return self.url.replace("ejlist.shtml", "ejlist_%d.shtml" % page_index)

    def get_content_list(self, _chrome):
        return _chrome.find_element_by_class_name("zwgklist").find_elements_by_tag_name("li")

    def get_content_info(self, _chrome, content):
        a = content.find_element_by_tag_name("a")
        public_date = content.find_element_by_tag_name("div").text
        title = str(public_date + "_" + a.get_attribute("title"))
        href = a.get_attribute("href")
        return title, href, public_date

    def get_content(self, _chrome):
        return _chrome.find_element_by_class_name("mb50").get_attribute('innerHTML')

    def get_ext_list(self, _chrome):
        return _chrome.find_element_by_class_name("fujian").find_elements_by_tag_name("a")
