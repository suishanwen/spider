from util.logger import Logger
from util import file, chrome
from model.Attachment import Attachment
from selenium.common.exceptions import NoSuchElementException
from page.NhcSt import NhcSt
from util.download import py_download
from conf.config import Const
from model.DownloadStatus import DownloadStatus
import time
import os


# 获取文章
def get_article(tmp_chrome, title, href, pub_time, page_info, page_name):
    dir_name = file.validate_title(
        title)
    Logger.info("requsts to : %s " % dir_name)
    # 打开原始链接
    tmp_chrome.get(href)
    time.sleep(1)
    # 检查是否正常打开页面
    code = page_info.check_content_status(tmp_chrome)
    if code == 404:
        Logger.info("404，文章不存在，跳过！")
        return
    elif code == 403:
        Logger.info("403，文章无权限查看，跳过！")
        return
    print("页面状态：\n{}".format(code))
    # 获取正文
    content = page_info.get_content(tmp_chrome)
    attachments = get_ext(tmp_chrome, page_info, dir_name, page_name)
    # 替换附件路径
    for attachment in attachments:
        content = file.replace_local_file(content, str(attachment.origin_file_name), attachment.local_path)
        content = page_info.replace_ext_url(content, attachment)
    full_path = '%s/index.html' % (os.path.abspath(".") + "/test")
    if file.write_to_file(full_path, content):
        Logger.info("摘取正文，保存页面成功！")
    print("共找到{}个附件".format(len(attachments)))
    download_attachments(attachments, tmp_chrome)


# 获取文章附件列表
def get_ext(tmp_chrome, page_info, dir_name, page_name):
    ext_list = []
    try:
        ext_list = page_info.get_ext_list(tmp_chrome)
    except NoSuchElementException:
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
            path = os.path.abspath(".") + "/test"
            full_path = "%s/%s" % (path, origin_file_name)
            local_ext_href = "." + full_path.replace(path, "")
            attachments.append(Attachment(href, origin_file_name, file_name, extension_name, full_path, local_ext_href))
    return attachments


def download_attachments(attachments, tmp_chrome):
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
            download_full_path = "%s/%s" % (Const.DOWNLOAD_PATH, attachment.origin_file_name)
            downloading_full_path = "%s/%s.crdownload" % (Const.DOWNLOAD_PATH, attachment.origin_file_name)
            try:
                tmp_chrome.get(attachment.url)
                time.sleep(1)
            except Exception as e:
                Logger.warning("%s chrome下载失败 %s！" % (attachment.url, str(e)))
            if file.downloads_done(attachment.origin_file_name) and file.move_file(download_full_path,
                                                                                   attachment.file_path):
                dl_count = 0
            else:
                file.remove_file(downloading_full_path)
        if dl_count == 0:
            Logger.info("附件下载成功！")
        else:
            Logger.warning("%s 附件下载失败!" % attachment.url)


_chrome = chrome.Chrome()
url = "http://www.nhc.gov.cn/bgt/2016dseqm/201804/09c7f62d1904423686769b6cf43808c9.shtml"
get_article(_chrome, "测试页面", url, "222", NhcSt(), "333")
_chrome.quit()
