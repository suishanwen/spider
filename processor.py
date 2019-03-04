import uuid
import time
import traceback
from util.yaml import yaml_read, yaml_write_pages
from conf.config import Const
from util import mysql, chrome, file
from util.logger import Logger
import selenium.common.exceptions
from util.download import py_download
from concurrent.futures import ThreadPoolExecutor, as_completed


# 获取所有分页页面
def get_page(page_info, page_index, page_name, page_url, page_exec):
    _chrome = chrome.Chrome()
    _chrome.get(page_url)
    time.sleep(1)
    page_count = page_info.get_page_count(_chrome)
    Logger.info("%s下共%d页!" % (page_name, page_count))
    if page_exec == 0:
        get_page_articles(_chrome, page_info, page_name)
        page_info.pages[page_index][2] = 1
        yaml_write_pages(Const.GOV_YAML, page_info.section, page_info.pages)
    _chrome.quit()
    for sub_page_index in range(2, page_count + 1):
        if sub_page_index <= page_exec:
            continue
        _chrome = chrome.Chrome()
        _chrome.get(page_info.get_sub_page_url(sub_page_index, page_url))
        time.sleep(1)
        get_page_articles(_chrome, page_info, page_name)
        _chrome.quit()
        page_info.pages[page_index][2] = sub_page_index
        yaml_write_pages(Const.GOV_YAML, page_info.section, page_info.pages)


# 获取分页下文章
def get_page_articles(_chrome, page_info, page_name):
    content_list = page_info.get_content_list(_chrome)
    tmp_chrome = chrome.Chrome()
    for i in range(len(content_list)):
        # 获取时间_标题、原始链接、发布时间
        title, href, pub_time = page_info.get_content_info(_chrome, content_list[i])
        # 检查是否已爬取
        if mysql.check_exist(title, href):
            Logger.info("%s(%s)已抓取,跳过" % (title, href))
            continue
        get_article(tmp_chrome, title, href, pub_time, page_info, page_name)
    Logger.info("当前页 %s 抓取完成 " % (_chrome.current_url()))
    tmp_chrome.quit()


# 获取文章
def get_article(tmp_chrome, title, href, pub_time, page_info, page_name):
    dir_name = file.validate_title(
        title)
    Logger.info("requsts to : %s " % dir_name)
    # 打开原始链接
    tmp_chrome.get(href)
    time.sleep(1)
    # 检查是否正常打开页面
    if page_info.check_content_not_exist(tmp_chrome):
        Logger.info("文章不存在，跳过！")
        mysql.set_toretry_task(str(uuid.uuid4()), page_info.pk_channel, href, title, pub_time, page_name,
                               "文章不存在，跳过！")
        return
    # 获取正文
    try:
        content = page_info.get_content(tmp_chrome)
        full_path = '%s/%s/%s/%s/index.html' % (Const.BASE_FILE_PATH, page_info.org_name, page_name, dir_name)
        if file.write_to_file(full_path, content):
            Logger.info("摘取正文，保存页面成功！")
            pk_article = str(uuid.uuid4())
            mysql.insert_html_record(pk_artcl=pk_article,
                                     pk_org=page_info.pk_org,
                                     pk_channel=page_info.pk_channel,
                                     title=title,
                                     src_url=str(href),
                                     path=full_path,
                                     pub_time=pub_time)
            Logger.info("写入文章数据成功！")
            get_ext(tmp_chrome, page_info, dir_name, pk_article, pub_time, page_name)
        else:
            mysql.set_toretry_task(str(uuid.uuid4()), page_info.pk_channel, href, title,
                                   pub_time, page_name, "正文保存失败！")
    except Exception as e:
        Logger.info("文章获取异常！%s" % tmp_chrome.current_url())
        mysql.set_toretry_task(str(uuid.uuid4()), page_info.pk_channel, href, title, pub_time, page_name,
                               "文章获取异常！{0}".format(str(e)).replace("'", '"'))


# 获取文章附件
def get_ext(tmp_chrome, page_info, dir_name, pk_article, pub_time, page_name):
    ext_list = []
    try:
        ext_list = page_info.get_ext_list(tmp_chrome)
    except selenium.common.exceptions.NoSuchElementException:
        Logger.info("未找到附件!")
    ext_fail = False
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
            url = tmp_chrome.current_url()
            url_prefix = url[0:url.rfind("/") + 1]
            file_name = "%s.%s" % (title, extension)
            path = '%s/%s/%s/%s' % (Const.BASE_FILE_PATH, page_info.org_name, page_name, dir_name)
            # 同目录下附件
            if href.find(url_prefix) != -1:
                full_path = "%s/%s" % (path, href.replace(url_prefix, ""))
            else:
                full_path = "%s/%s" % (path, origin_file_name)
            dl_count = 1
            while 1 <= dl_count <= 10:
                try:
                    Logger.warning("%s 开始第%d次断点下载！" % (href, dl_count))
                    if py_download(href, full_path):
                        dl_count = 0
                    else:
                        Logger.warning("检测到文件状态有误，重新开始！")
                except Exception as e:
                    dl_count += 1
                    Logger.warning("%s [异常]断点下载失败 %s！" % (href, str(e)))
                    time.sleep(3)
            if dl_count > 10:
                download_full_path = "%s/%s" % (Const.DOWNLOAD_PATH, origin_file_name)
                try:
                    ext.click()
                    time.sleep(1)
                except Exception as e:
                    Logger.warning("%s chrome下载失败 %s！" % (href, str(e)))
                if file.downloads_done(file_name) and file.move_file(download_full_path, full_path):
                    dl_count = 0
            if dl_count == 0:
                mysql.insert_mapping(pk_artcl_file=str(uuid.uuid4()),
                                     pk_artcl=pk_article,
                                     file_type_name=extension,
                                     file_name=file_name,
                                     file_path=full_path)
                Logger.info("写入文章附件mapping成功！")
            else:
                Logger.warn("%s 附件下载失败!" % href)
                if not ext_fail:
                    mysql.set_toretry_task(str(uuid.uuid4()), page_info.pk_channel, url, title, pub_time, page_name,
                                           "附件下载失败！")
                    ext_fail = True


# 异常抓取重试任务
def retry_failed(page_info):
    Logger.info("开始重试任务...")
    retry_list = mysql.query_toretry_task(page_info.pk_channel)
    _chrome = chrome.Chrome()
    for retry_info in retry_list:
        get_article(_chrome, retry_info["title"], retry_info["src_url"], retry_info["pub_time"], page_info,
                    retry_info["sub_channel_name"])
        # 如果任务未失败（retry_info未增加）,删除任务
        mysql.delete_toretry_task(page_info.pk_channel, retry_info["src_url"], retry_info["total_times"])
    # 停止重试超过5次的任务
    mysql.stop_toretry_task(page_info.pk_channel)
    _chrome.quit()
    Logger.info("重试任务完成")


# 顺序抓取
def normal_start(page_info):
    Logger.info("开始多线程[%d]顺序抓取..." % page_info.max_thread)
    task_list = []
    with ThreadPoolExecutor(page_info.max_thread) as executor:
        for page_index in range(len(page_info.pages)):
            page = page_info.pages[page_index]
            page_name = page[0]
            page_url = page_info.domain + page[1]
            try:
                page_exec = page[2]
            except IndexError:
                page_exec = 0
            task = executor.submit(get_page, page_info, page_index, page_name, page_url, page_exec)
            task_list.append(task)
        for task in as_completed(task_list):
            Logger.info("线程[%s]执行完成" % str(task))


def __main__(page_info):
    Logger.info("程序启动")
    page_info.from_dict(yaml_read(Const.GOV_YAML, ("gov", page_info.section)))
    page_info.pk_org = mysql.get_pk_org(page_info.org_name)
    page_info.pk_channel = mysql.get_pk_channel(page_info.pk_org, page_info.channel)
    Logger.info("查询机构信息成功，开始抓取数据...")
    retry_failed(page_info)
    try:
        normal_start(page_info)
    except Exception as e:
        Logger.error("未捕获的异常%s\n%s" % (str(e), traceback.format_exc()))
    Logger.info("本次程序执行完成,退出!")
