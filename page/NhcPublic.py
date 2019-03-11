from page.PageInfo import PageInfo
from util import file


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
        return "http://www.nhc.gov.cn/xxgk/getManuscriptByType_manuscript.action?pagedata.pageNum=%d" % page_index

    def get_content_list(self, _chrome):
        return _chrome.chrome.find_element_by_tag_name("table").find_elements_by_tag_name("tr")[3:8]

    def get_content_info(self, _chrome, content):
        a = content.find_element_by_tag_name("a")
        public_date = content.find_elements_by_tag_name("td")[2].text
        title = str(a.text)
        href = a.get_attribute("href")
        manuscript_id = href[href.find("'") + 1:href.rfind("'")]
        static_url = "http://www.nhc.gov.cn" + \
                     _chrome.chrome.find_element_by_id("staticUrl_" + manuscript_id).get_attribute('value')
        return title, static_url, public_date

    def check_content_status(self, _chrome):
        content = _chrome.page_source()
        code = 200
        if content.find('<h1>Not Found</h1>') != -1:
            code = 404
        elif content.find('<h1>Forbidden</h1>') != -1:
            code = 403
        return code

    def get_content(self, _chrome):
        return _chrome.multi_find_class(["content", "mb50", "wrap", "w1100"]).get_attribute('innerHTML')

    def get_ext_list(self, _chrome):
        con_classes = ["con", "content"]
        ext_a_list = []
        for _class in con_classes:
            for ext in _chrome.chrome.find_elements_by_class_name(_class):
                ext_a_list += ext.find_elements_by_tag_name("a")
        return ext_a_list

    def replace_ext_url(self, content, attachment):
        return file.replace_local_file(content, attachment.file_name[
                                                0:attachment.file_name.rfind(
                                                    ".")] + "_s" + "." + attachment.file_type_name,
                                       attachment.local_path)
