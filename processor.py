import uuid
import time
import traceback
import selenium.common.exceptions
from conf.config import Const
from util import mysql, chrome, file
from util.logger import Logger
from util.download import py_download
from concurrent.futures import ThreadPoolExecutor, as_completed
from model.Attachment import Attachment
from model.DownloadStatus import DownloadStatus
from selenium.common.exceptions import NoSuchElementException


# 获取所有分页页面
def get_page(spider, channel):
    _chrome = chrome.Chrome()
    _chrome.get(channel.web_site_url)
    time.sleep(1)
    try:
        page_count = spider.get_page_count(_chrome)
    except NoSuchElementException:
        page_count = 1
    try:
        Logger.info("%s下共%d页!" % (channel.channel_name, page_count))
        exist = get_page_articles(_chrome, spider, channel)
        if channel.scrapy_page == 0:
            mysql.update_scrapy_page(channel.pk_channel, 1)
        _chrome.quit()
        for sub_page_index in range(2, page_count + 1):
            # 断页续抓
            if sub_page_index <= channel.scrapy_page and exist:
                continue
            _chrome = chrome.Chrome()
            _chrome.get(spider.get_sub_page_url(sub_page_index, channel.web_site_url))
            time.sleep(1)
            exist = get_page_articles(_chrome, spider, channel)
            _chrome.quit()
            # 增量抓取 并 连续3页出现已抓取 = 抓取完毕
            if exist and (sub_page_index + channel.scrapy_page) > page_count + 3:
                Logger.info("增量抓取并连续3页出现已抓取,抓取完毕")
                mysql.update_scrapy_page(channel.pk_channel, page_count)
                break
            mysql.update_scrapy_page(channel.pk_channel, sub_page_index)
    except Exception as e:
        Logger.error("未处理的异常：%s \n%s" % (str(e), traceback.format_exc()))


# 获取分页下文章
def get_page_articles(_chrome, spider, channel):
    content_list = spider.get_content_list(_chrome)
    tmp_chrome = chrome.Chrome()
    # 当前页是否存在已抓取
    exist = False
    for i in range(len(content_list)):
        # 获取时间_标题、原始链接、发布时间
        title, href, pub_time = spider.get_content_info(_chrome, content_list[i])
        # 检查是否已爬取
        if mysql.check_exist(title, href):
            Logger.info("%s(%s)已抓取,跳过" % (title, href))
            exist = True
            continue
        get_article(tmp_chrome, title, href, pub_time, spider, channel)
    Logger.info("当前页 %s 抓取完成 " % (_chrome.current_url()))
    tmp_chrome.quit()
    return exist


# 获取文章
def get_article(tmp_chrome, title, href, pub_time, spider, channel):
    dir_name = file.validate_title(
        title)
    Logger.info("requsts to : %s " % dir_name)
    # 打开原始链接
    tmp_chrome.get(href)
    time.sleep(1)
    # 检查是否正常打开页面
    code = spider.check_content_status(tmp_chrome)
    if code == 404:
        Logger.info("404，文章不存在，跳过！")
        mysql.set_toretry_task(str(uuid.uuid4()), channel.pk_channel, href, title, pub_time,
                               "404，文章不存在，跳过！")
        return
    elif code == 403:
        Logger.info("403，文章无权限查看，跳过！")
        mysql.set_toretry_task(str(uuid.uuid4()), channel.pk_channel, href, title, pub_time,
                               "403，文章无权限查看，跳过！")
        return
    elif code == 503:
        Logger.info("503,Service Unavailable，重试！")
        get_article(tmp_chrome, title, href, pub_time, spider, channel)
        return
    # 获取正文
    try:
        pk_article = mysql.get_pk_article(href, title)
        content = spider.get_content(tmp_chrome)
        attachments = get_ext(tmp_chrome, spider, channel, dir_name)
        # 替换附件路径
        for attachment in attachments:
            content = file.replace_local_file(content, str(attachment.origin_file_name), attachment.local_path)
            content = spider.replace_ext_url(content, attachment)
        full_path = '%s/%s/%s/%s/index.html' % (Const.BASE_FILE_PATH, channel.org_name, channel.channel_name, dir_name)
        if file.write_to_file(full_path, content):
            Logger.info("摘取正文，保存页面成功！")
            mysql.insert_html_record(pk_artcl=pk_article,
                                     pk_org=channel.pk_org,
                                     pk_channel=channel.pk_channel,
                                     title=title,
                                     src_url=href,
                                     path=full_path,
                                     pub_time=pub_time)
            Logger.info("写入文章数据成功！")
            download_attachments(attachments, channel.pk_channel, pk_article, href, title, pub_time, tmp_chrome)
        else:
            mysql.set_toretry_task(str(uuid.uuid4()), channel.pk_channel, href, title,
                                   pub_time, "正文保存失败！")
    except Exception as e:
        Logger.info("文章获取异常！%s :%s" % (tmp_chrome.current_url(), str(e)))
        mysql.set_toretry_task(str(uuid.uuid4()), channel.pk_channel, href, title, pub_time,
                               "文章获取异常！{0}".format(traceback.format_exc()).replace("'", '"'))


# 获取文章附件列表
def get_ext(tmp_chrome, spider, channel, dir_name):
    ext_list = []
    try:
        ext_list = spider.get_ext_list(tmp_chrome)
    except selenium.common.exceptions.NoSuchElementException:
        Logger.info("未找到附件!")
    attachments = []
    for ext in ext_list:
        href = ext.get_attribute('href')
        if href and file.is_appendix_file(href):
            extension_name = file.get_file_extension(href)
            title = ext.text
            origin_file_name = href[href.rfind("/") + 1: len(href)]
            if not title:
                title = origin_file_name
            if title.find('.%s' % extension_name) != -1:
                title = title.replace('.%s' % extension_name, "")
            file_name = "%s.%s" % (title, extension_name)
            path = '%s/%s/%s/%s' % (Const.BASE_FILE_PATH, channel.org_name, channel.channel_name, dir_name)
            full_path = "%s/%s" % (path, origin_file_name)
            local_ext_href = "." + full_path.replace(path, "")
            attachments.append(Attachment(href, origin_file_name, file_name, extension_name, full_path, local_ext_href))
    return attachments


def download_attachments(attachments, pk_channel, pk_article, article_url, article_title, pub_time, tmp_chrome):
    # 标识是否失败过、一个文章只存一次失败记录
    ext_fail = False
    for attachment in attachments:
        dl_count = 1
        # 下载方式一 读取Content-Lenth 断点下载
        while 1 <= dl_count <= 10:
            try:
                Logger.warning("%s->%s 开始第%d次断点下载！" % (attachment.url, attachment.file_path, dl_count))
                status, code = py_download(attachment.url, attachment.file_path)
                if status:
                    dl_count = 0
                else:
                    dl_status = DownloadStatus.get(code)
                    if dl_status:
                        if dl_status[0]:
                            break
                        else:
                            Logger.warning(dl_status[1])
                            mysql.set_toretry_task(str(uuid.uuid4()), pk_channel, article_url, article_title, pub_time,
                                                   dl_status[1])
                            return
                    else:
                        Logger.warning("下载未成功，重新开始！")
                    dl_count += 1
            except Exception as e:
                dl_count += 1
                Logger.warning("%s [异常]断点下载失败 %s！" % (attachment.url, str(e)))
                time.sleep(3)
        if dl_count != 0:
            # 下载方式二 chromeDriver下载,支持chunked
            Logger.info("开始chromeDriver下载：%s" % attachment.url)
            download_full_path = "%s/%s" % (Const.DOWNLOAD_PATH, attachment.origin_file_name)
            downloading_full_path = "%s/%s.crdownload" % (Const.DOWNLOAD_PATH, attachment.origin_file_name)
            try:
                file.remove_file(downloading_full_path)
                tmp_chrome.get(attachment.url)
                time.sleep(1)
                if file.downloads_done(attachment.origin_file_name) and file.move_file(download_full_path,
                                                                                       attachment.file_path):
                    dl_count = 0
            except Exception as e:
                Logger.warning("%s chrome下载失败 %s！" % (attachment.url, str(e)))
                file.remove_file(downloading_full_path)
        if dl_count == 0:
            mysql.insert_mapping(pk_artcl_file=str(uuid.uuid4()),
                                 pk_artcl=pk_article,
                                 file_type_name=attachment.file_type_name,
                                 file_name=attachment.file_name,
                                 file_path=attachment.file_path)
            Logger.info("写入文章附件mapping成功！")
        else:
            Logger.warning("%s 附件下载失败!" % attachment.url)
            if not ext_fail:
                mysql.set_toretry_task(str(uuid.uuid4()), pk_channel, article_url, article_title, pub_time,
                                       "附件下载失败！")
                ext_fail = True


# 异常抓取重试任务
def retry_failed(spider, channel):
    Logger.info("开始重试任务...")
    retry_list = mysql.query_toretry_task(channel.pk_channel)
    _chrome = chrome.Chrome()
    for retry_info in retry_list:
        get_article(_chrome, retry_info["title"], retry_info["src_url"], retry_info["pub_time"], spider, channel)
        # 如果任务未失败（retry_info未增加）,删除任务
        mysql.delete_toretry_task(channel.pk_channel, retry_info["src_url"], retry_info["total_times"])
    # 停止重试超过5次的任务
    mysql.stop_toretry_task(channel.pk_channel)
    _chrome.quit()
    Logger.info("重试任务完成")


# 线程池启动抓取
def startup(spider):
    max_thread = len(spider.channels)
    if max_thread > 3:
        max_thread = 3
    Logger.info("开始多线程[%d]顺序抓取..." % max_thread)
    task_list = []
    with ThreadPoolExecutor(max_thread) as executor:
        for channel in spider.channels:
            # 异常抓取重试任务
            task = executor.submit(retry_failed, spider, channel)
            task_list.append(task)
            # 正常抓取
            task = executor.submit(get_page, spider, channel)
            task_list.append(task)
        for task in as_completed(task_list):
            Logger.info("线程[%s]执行完成" % str(task))


def __main__(spider):
    Logger.info("%s 启动~" % str(spider))
    startup(spider)
    Logger.info("%s 执行完成,退出!" % str(spider))
