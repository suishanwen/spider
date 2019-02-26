import logging
import uuid
import time
from util.yaml import yaml_read
from conf.config import Const
from util import mysql, chrome, file

log_filename = "logging.log"
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s [%(funcName)s: %(filename)s, %(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filemode='a')


# 获取所有分页页面
def get_page():
    _chrome = chrome.get_chrome()
    _chrome.get(url)
    time.sleep(1)
    text = _chrome.find_element_by_class_name("pagination_index_last").text
    page_count = int(text[text.find("共") + 2:text.find("页") - 1])
    get_article(_chrome)
    _chrome.quit()
    for i in range(page_count):
        page_index = i + 1
        if page_index == 1:
            continue
        page_url = url.replace("ejlist.shtml", "ejlist_%d.shtml" % page_index)
        _chrome = chrome.get_chrome()
        _chrome.get(page_url)
        time.sleep(1)
        get_article(_chrome)
        _chrome.quit()


# 获取分页下文章
def get_article(_chrome):
    li_list = _chrome.find_element_by_class_name("zwgklist").find_elements_by_tag_name("li")
    tmp_chrome = chrome.get_chrome()
    for i in range(len(li_list)):
        a = li_list[i].find_element_by_tag_name("a")
        public_date = li_list[i].find_element_by_tag_name("div").text
        title = str(public_date + "_" + a.get_attribute("title"))
        dir_name = file.validate_title(
            title)
        href = a.get_attribute("href")
        logging.info("requsts to : %s ", dir_name)
        tmp_chrome.get(href)
        time.sleep(1)
        content = tmp_chrome.find_element_by_class_name("mb50").get_attribute('innerHTML')
        full_path = '%s/%s/%s/%s/index.html' % (Const.BASE_FILE_PATH, org, name, dir_name)
        if file.write_to_file(full_path, content):
            logging.info("摘取正文，保存页面成功！")
        pk_article = str(uuid.uuid4())
        mysql.insert_html_record(pk_artcl=pk_article,
                                 pk_org=org,
                                 title=title,
                                 src_url=str(tmp_chrome.current_url),
                                 path=full_path,
                                 pub_time=public_date)
        logging.info("写入文章数据成功！")
        get_ext(tmp_chrome, dir_name, pk_article)
    tmp_chrome.quit()
    logging.info("snatch at %s successful , prepared to next", _chrome.current_url)


# 获取文章附件
def get_ext(tmp_chrome, dir_name, pk_article):
    ext_list = []
    try:
        ext_list = tmp_chrome.find_element_by_class_name("fujian").find_elements_by_tag_name("a")
    except Exception as e:
        logging.info("未找到附件!")
    for ext in ext_list:
        href = ext.get_attribute('href')
        if file.is_appendix_file(href):
            extension = file.get_file_extension(href)
            title = ext.text
            if title.find('.%s' % extension) != -1:
                title = title.replace('.%s' % extension, "")
            file_name = "%s.%s" % (title, extension)
            path = '%s/%s/%s/%s' % (Const.BASE_FILE_PATH, org, name, dir_name)
            local_file_name = href[href.rfind("/") + 1: len(href)]
            download_full_path = "%s/%s" % (Const.DOWNLOAD_PATH, local_file_name)
            full_path = "%s/%s" % (path, file_name)
            ext.click()
            time.sleep(1)
            file.downloads_done()
            file.move_file(download_full_path, full_path)
            mysql.insert_mapping(pk_artcl_file=str(uuid.uuid4()),
                                 pk_artcl=pk_article,
                                 file_type_name=extension,
                                 file_name=file_name,
                                 file_path=full_path)
            logging.info("写入文章附件mapping成功！")


if __name__ == '__main__':
    org = yaml_read(Const.GOV_YAML, ("gov", "hncStat", "org"))
    domain = yaml_read(Const.GOV_YAML, ("gov", "hncStat", "url"))
    pages = yaml_read(Const.GOV_YAML, ("gov", "hncStat", "pages"))
    for page in pages:
        name = page[0]
        url = domain + page[1]
        get_page()
