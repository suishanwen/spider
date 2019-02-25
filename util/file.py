import logging

import requests
import os, re

file_suffix = ["png", "pdf", "xls", "xlsx", "doc", "docx", "jpg", "zip", "txt", "wps", "bmp", "ppt", "pptx"]

log_filename = 'logging.log'
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s [%(funcName)s: %(filename)s, %(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filemode='a')


def mkdir(path):
    # 去除左右两边的空格
    path = path.strip()
    # 去除尾部 \符号
    path = path.rstrip("\\")

    if not os.path.exists(path):
        os.makedirs(path)

    return path


def save_file(path, file_name, data):
    if data == None:
        return

    mkdir(path)
    if (not path.endswith("/")):
        path = path + "/"
    file = open(path + file_name, "wb")
    file.write(data)
    file.flush()
    file.close()





# 判断文件是否存在，如果不存在则创建新的文件夹
def is_dir_exists(file_dir):
    if not os.path.exists(file_path + "/" + file_dir):
        os.makedirs(file_path + "/" + file_dir)
    return True


def validate_title(title):
    r_str = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(r_str, "", title)  # 替换为下划线
    return new_title.replace("\t", "").replace("\r", "").replace("\n", "").replace(" ", "").replace(".", "")


def get_file_extension(filename):
    arr = os.path.splitext(filename)
    return arr[len(arr) - 1].replace(".", "")


def write_file(r, file_name):
    is_dir_exists("")
    file_dir = file_path + "\\files\\" + file_name
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


