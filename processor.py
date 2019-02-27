import uuid
import time
from util.yaml import yaml_read, yaml_write_pages
from conf.config import Const
from util import mysql, chrome, file
from util.logger import Logger
import selenium.common.exceptions
from util.download import py_download


# 获取所有分页页面
def get_page(page_info):
    _chrome = chrome.Chrome()
    _chrome.get(page_info.url)
    time.sleep(1)
    page_count = page_info.get_page_count(_chrome)
    if page_info.page_exec == 0:
        get_article(_chrome, page_info)
        page_info.pages[page_info.index][2] = 1
        yaml_write_pages(Const.GOV_YAML, page_info.section, page_info.pages)
    _chrome.quit()
    for page_index in range(2, page_count + 1):
        if page_index <= page_info.page_exec:
            continue
        _chrome = chrome.Chrome()
        _chrome.get(page_info.get_sub_page_url(page_index))
        time.sleep(1)
        get_article(_chrome, page_info)
        _chrome.quit()
        page_info.pages[page_info.index][2] = page_index
        yaml_write_pages(Const.GOV_YAML, page_info.section, page_info.pages)


# 获取分页下文章
def get_article(_chrome, page_info):
    content_list = page_info.get_content_list(_chrome)
    tmp_chrome = chrome.Chrome()
    for i in range(len(content_list)):
        # 获取时间_标题、原始链接、发布时间
        title, href, public_date = page_info.get_content_info(_chrome, content_list[i])
        # 检查是否已爬取
        if mysql.check_exist(title, href):
            Logger.info("%s(%s)已抓取,跳过" % (title, href))
            continue
        dir_name = file.validate_title(
            title)
        Logger.info("requsts to : %s " % dir_name)
        # 打开原始链接
        tmp_chrome.get(href)
        time.sleep(1)
        # 检查是否正常打开页面
        if page_info.check_content_not_exist(tmp_chrome):
            Logger.info("文章不存在，跳过！")
            continue
        # 获取正文
        content = page_info.get_content(tmp_chrome)
        full_path = '%s/%s/%s/%s/index.html' % (Const.BASE_FILE_PATH, page_info.org_name, page_info.name, dir_name)
        if file.write_to_file(full_path, content):
            Logger.info("摘取正文，保存页面成功！")
        pk_article = str(uuid.uuid4())
        mysql.insert_html_record(pk_artcl=pk_article,
                                 pk_org=page_info.pk_org,
                                 pk_channel=page_info.pk_channel,
                                 title=title,
                                 src_url=str(tmp_chrome.current_url()),
                                 path=full_path,
                                 pub_time=public_date)
        Logger.info("写入文章数据成功！")
        get_ext(tmp_chrome, page_info, dir_name, pk_article)
    Logger.info("当前页 %s 抓取完成 " % (_chrome.current_url()))
    tmp_chrome.quit()


# 获取文章附件
def get_ext(tmp_chrome, page_info, dir_name, pk_article):
    ext_list = []
    try:
        ext_list = page_info.get_ext_list(tmp_chrome)
    except selenium.common.exceptions.NoSuchElementException:
        Logger.info("未找到附件!")
    for ext in ext_list:
        href = ext.get_attribute('href')
        if href and file.is_appendix_file(href):
            extension = file.get_file_extension(href)
            title = ext.text
            origin_file_name = href[href.rfind("/") + 1: len(href)]
            if not title:
                title = origin_file_name
            if title.find('.%s' % extension) != -1:
                title = title.replace('.%s' % extension, "")
            file_name = "%s.%s" % (title, extension)
            path = '%s/%s/%s/%s' % (Const.BASE_FILE_PATH, page_info.org_name, page_info.name, dir_name)
            download_full_path = "%s/%s" % (Const.DOWNLOAD_PATH, origin_file_name)
            full_path = "%s/%s" % (path, file_name)
            # try:
            #     ext.click()
            #     time.sleep(1)
            # except Exception:
            #     Logger.warning("%s chrome下载失败！" % href)
            # if not file.downloads_done(file_name):
            dl_count = 1
            while 1 <= dl_count <= 10:
                try:
                    Logger.warning("%s 开始第%d次断点下载！" % (href, dl_count))
                    if py_download(href, download_full_path):
                        dl_count = 0
                except Exception:
                    Logger.warning("%s 断点下载失败！" % href)
                    time.sleep(3)
            if file.move_file(download_full_path, full_path):
                mysql.insert_mapping(pk_artcl_file=str(uuid.uuid4()),
                                     pk_artcl=pk_article,
                                     file_type_name=extension,
                                     file_name=file_name,
                                     file_path=full_path)
                Logger.info("写入文章附件mapping成功！")


def __main__(page_info):
    page_info.org_name = yaml_read(Const.GOV_YAML, ("gov", page_info.section, "org"))
    page_info.domain = yaml_read(Const.GOV_YAML, ("gov", page_info.section, "url"))
    page_info.web_site_url = yaml_read(Const.GOV_YAML, ("gov", page_info.section, "web_site_url"))
    page_info.pages = yaml_read(Const.GOV_YAML, ("gov", page_info.section, "pages"))
    page_info.pk_org = mysql.get_pk_org(page_info.org_name)
    page_info.pk_channel = mysql.get_pk_channel(page_info.pk_org, page_info.web_site_url)
    for index in range(len(page_info.pages)):
        page = page_info.pages[index]
        page_info.index = index
        page_info.name = page[0]
        page_info.url = page_info.domain + page[1]
        page_info.page_exec = page[2]
        get_page(page_info)
