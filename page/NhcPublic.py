from page.PageInfo import PageInfo


class NhcPublic(PageInfo):

    def __init__(self):
        PageInfo.__init__(self)
        self.section = "nhcPublic"

    def get_page_count(self, _chrome):
        text = _chrome.chrome.find_element_by_id("TDLASTPAGE") \
            .find_element_by_tag_name("a").get_attribute('href')
        page_count = int(text[text.find("(") + 1:text.find(")")])
        return page_count

    def get_sub_page_url(self, page_index, page_url):
        return "%s/getManuscriptByType_manuscript.action?pagedata.pageNum = %d" % (page_url, page_index)

    def get_content_list(self, _chrome):
        return _chrome.chrome.find_element_by_tag_name("table").find_elements_by_tag_name("tr")[3:8]

    def get_content_info(self, _chrome, content):
        a = content.find_element_by_tag_name("a")
        public_date = content.find_elements_by_tag_name("td")[2].text
        title = str(public_date + "_" + a.text)
        href = a.get_attribute("href")
        manuscript_id = href[href.find("'") + 1:href.rfind("'")]
        static_url = "http://www.nhc.gov.cn" + \
                     _chrome.chrome.find_element_by_id("staticUrl_" + manuscript_id).get_attribute('value')
        return title, static_url, public_date

    def check_content_not_exist(self, _chrome):
        return _chrome.page_source().find('<h1>Not Found</h1>') != -1

    def get_content(self, _chrome):
        return _chrome.multi_find_class(["content", "mb50", "w1100"]).get_attribute('innerHTML')

    def get_ext_list(self, _chrome):
        return _chrome.chrome.find_element_by_class_name("con").find_elements_by_tag_name("a")
