from page.PageInfo import PageInfo


class Beijing(PageInfo):
    section = "beijing"

    def get_page_count(self, _chrome):
        return int(_chrome.find_element_by_class_name("laypage_last").get_attribute('data-page'))

    def get_sub_page_url(self, _chrome, page_index):
        return "%s#!page=%d" % (self.url, page_index)

    def get_content_list(self, _chrome):
        return _chrome.find_element_by_class_name("zxgklist").find_elements_by_tag_name("li")

    def get_content_info(self, _chrome, content):
        a = content.find_element_by_tag_name("a")
        public_date = content.find_element_by_class_name("date").text
        title = str(public_date + "_" + a.get_attribute("title"))
        href = a.get_attribute("href")
        return title, href, public_date

    def get_content(self, _chrome):
        return _chrome.find_element_by_class_name("content_con").get_attribute('innerHTML')

    def get_ext_list(self, _chrome):
        return _chrome.find_element_by_class_name("fujian").find_elements_by_tag_name("a")
