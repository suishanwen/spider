from util.logger import Logger
from util import file, chrome
from conf.config import Const
from model.Attachment import Attachment
from selenium.common.exceptions import NoSuchElementException
from page.NhcSt import NhcSt
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
        content = file.replace_local_file(content, str(attachment.file_name), attachment.local_path)
        content = page_info.replace_ext_url(content, attachment)
    full_path = '%s/index.html' % (os.path.abspath(".") + "/test")
    if file.write_to_file(full_path, content):
        Logger.info("摘取正文，保存页面成功！")
    print("共找到{}个附件".format(len(attachments)))


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
            path = '%s/%s/%s/%s' % (Const.BASE_FILE_PATH, page_info.org_name, page_name, dir_name)
            full_path = "%s/%s" % (path, origin_file_name)
            local_ext_href = "." + full_path.replace(path, "")
            attachments.append(Attachment(href, origin_file_name, file_name, extension_name, full_path, local_ext_href))
    return attachments


_chrome = chrome.Chrome()
get_article(_chrome, "测试页面", "http://www.gov.cn/zhengce/content/2018-05/16/content_5291243.htm", "222", NhcSt(), "333")
_chrome.quit()
