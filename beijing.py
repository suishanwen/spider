import logging
import uuid
from util.yaml import yaml_read
from conf.config import Const
from util import utils, mysql, chrome

log_filename = "logging.log"
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s [%(funcName)s: %(filename)s, %(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filemode='a')


# 获取所有分页页面
def get_page():
    _chrome = chrome.get_chrome()
    _chrome.get(url)
    page_count = int(_chrome.find_element_by_class_name("laypage_last").get_attribute('data-page'))
    _chrome.quit()
    for i in range(page_count):
        page_index = i + 1
        page_url = "%s#!page=%d" % (url, page_index)
        _chrome = chrome.get_chrome()
        _chrome.get(page_url)
        get_article(_chrome)
        _chrome.quit()


# 获取分页下文章
def get_article(_chrome):
    li_list = _chrome.find_element_by_class_name("zxgklist").find_elements_by_tag_name("li")
    tmp_chrome = utils.get_chrome()
    for i in range(len(li_list)):
        a = li_list[i].find_element_by_tag_name("a")
        public_date = li_list[i].find_element_by_class_name("date").text
        title = str(public_date + "_" + a.get_attribute("title"))
        dir_name = utils.validate_title(
            title)
        href = a.get_attribute("href")
        logging.info("requsts to : %s ", dir_name)
        tmp_chrome.get(href)
        content = tmp_chrome.find_element_by_class_name("content_con").get_attribute('innerHTML')
        full_path = '%s/%s/%s/%s/index.html' % (Const.BASE_FILE_PATH, url, name, dir_name)
        if utils.write_to_file(full_path, content):
            logging.info("write to file successful")
        mysql.insert_html_record(pk_artcl=str(uuid.uuid4()),
                                 title=title,
                                 src_url=str(tmp_chrome.current_url),
                                 path=full_path,
                                 pub_time=public_date)
    tmp_chrome.quit()
    logging.info("snatch at %s successful , prepared to next", _chrome.current_url)


if __name__ == '__main__':
    domain = yaml_read(Const.GOV_YAML, ("gov", "beijing", "url"))
    pages = yaml_read(Const.GOV_YAML, ("gov", "beijing", "pages"))
    for page in pages:
        name = page[0]
        url = domain + page[1]
        get_page()
