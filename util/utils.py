import logging

import requests
from selenium import webdriver
import os, sys, re, time, datetime

log_filename = 'logging.log'
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s [%(funcName)s: %(filename)s, %(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filemode='a')

d = os.path.dirname(__file__)
base_file_path = "%s/file" % os.path.dirname(d)
html_header = "<html lang=\"zh-cn\"><head><meta charset=\"utf-8\"/></head><body>"
html_footer = "</body></html>"
file_suffix = ["png", "pdf", "xls", "xlsx", "doc", "docx", "jpg", "zip", "txt", "wps", "bmp", "ppt", "pptx"]


def get_chrome():
    option = webdriver.ChromeOptions()
    option.add_argument("--headless")
    # return webdriver.Chrome(
    #     chrome_options=option)
    return webdriver.Chrome()


def mkdir(path):
    # 去除左右两边的空格
    path = path.strip()
    # 去除尾部 \符号
    path = path.rstrip("/")

    if not os.path.exists(path):
        os.makedirs(path)

    return path


def save_file(path, file_name, data):
    if not data:
        return
    mkdir(path)
    if not path.endswith("/"):
        path = path + "/"
    file = open(path + file_name, "wb")
    file.write(data)
    file.flush()
    file.close()


# 将一个文件写到本地目录
def write_to_file(full_path, text):
    path = full_path[0:full_path.rfind("/")]
    if text:
        content = text
        # 如果是html，则给text拼接一个卡头和结尾
        if str.endswith(full_path, "html", 0, len(full_path)):
            content = html_header + text + html_footer
        mkdir(path)
        with open(full_path, mode="w", encoding="utf-8") as file:
            file.write(content)
        return True
    else:
        return False


def validate_title(title):
    r_str = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(r_str, "", title)  # 替换为下划线
    return new_title.replace("\t", "").replace("\r", "").replace("\n", "").replace(" ", "").replace(".", "")


def get_file_extension(filename):
    arr = os.path.splitext(filename)
    return arr[len(arr) - 1].replace(".", "")


def write_file(r, file_name):
    file_dir = base_file_path + "\\files\\" + file_name
    try:
        with open(file=file_dir, mode="wb") as file:
            for line in r.iter_content(chunk_size=1024):
                if line:
                    file.write(line)
        r.close()
    except requests.exceptions.ConnectionError:
        logging.warning("not fond iter_content")
    else:
        logging.info("write file %s finished, prepared to next", file_name)


def is_appendix_file(url):
    extension = str(get_file_extension(url)).lower()
    if extension and extension in file_suffix:
        return True
    else:
        return False


if __name__ == '__main__':
    chrome = get_chrome()
    chrome.get("http://www.baidu.com")
