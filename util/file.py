import logging
from urllib3.exceptions import NewConnectionError
import requests
import os, re
import shutil
import time
from conf.config import Const

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
        if str.endswith(full_path, "html", 0, len(full_path)) and text.find("<body") == -1:
            content = html_header + text + html_footer
        mkdir(path)
        with open(full_path, mode="w", encoding="utf-8") as file:
            file.write(content)
        return True
    else:
        return False


def validate_title(title):
    r_str = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    title_dir = re.sub(r_str, "", title)  # 替换为空
    spec_char = ["\u3000", "\t", "\r", "\n", " ", ".", "【", "】", "；", "'", "《", "》", "，", "（", "）", "〔", "〕", "：", ":"]
    for c in spec_char:
        title_dir = title_dir.replace(c, "_")
    if len(title_dir) > 30:
        title_dir = title_dir[0:30]
    return title_dir


def get_file_extension(filename):
    arr = os.path.splitext(filename)
    return arr[len(arr) - 1].replace(".", "")


def write_file(r, full_path):
    path = full_path[0:full_path.rfind("/")]
    mkdir(path)
    try:
        with open(file=full_path, mode="wb") as file:
            for line in r.iter_content(chunk_size=1024):
                if line:
                    file.write(line)
        r.close()
    except requests.exceptions.ConnectionError:
        logging.warning("not fond iter_content")
    else:
        logging.info("write file %s finished, prepared to next", full_path)


def is_appendix_file(url):
    extension = str(get_file_extension(url)).lower()
    if extension and extension in file_suffix:
        return True
    else:
        return False


def get_file(url):
    if re.match(r'^https?:/{2}\w.+$', url):
        s = requests.session()
        s.keep_alive = False
        try:
            return requests.get(url, timeout=10, stream=True)
        except NewConnectionError:
            return ''
        except requests.exceptions.ConnectionError:
            return ''
        except requests.exceptions.RequestException:
            return ''
    else:
        logging.error('invalid url for %s', url)


def move_file(src_file, dst_file):
    if not os.path.isfile(src_file):
        logging.error("%s not exist!" % (src_file))
        return False
    else:
        fpath, fname = os.path.split(dst_file)  # 分离文件名和路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)  # 创建路径
        shutil.move(src_file, dst_file)  # 移动文件
        logging.info("移动下载文件，归档重命名 %s -> %s" % (src_file, dst_file))
        return True


def downloads_done(file_name):
    succ = False
    for i in os.listdir(Const.DOWNLOAD_PATH):
        if file_name + ".crdownload" in i:
            time.sleep(1)
            return downloads_done(file_name)
        if file_name in i:
            succ = True
    if succ:
        logging.info("chrome下载附件完成！")
    else:
        logging.info("chrome下载附件失败！")
    return succ


def replace_local_file(content, file_name, local_path):
    _len = len(file_name)
    end = content.find(file_name)
    while end != -1:
        part = content[0:end + _len]
        start = part.rfind("\"")
        remote_path = part[start + 1:end + _len]
        print(remote_path)
        content = content.replace(remote_path, local_path)
        end = content.find(file_name, end + _len)
    return content


def remove_file(downloading_file_path):
    if os.path.isfile(downloading_file_path):
        os.remove(downloading_file_path)
    else:
        print("要删除的文件不存在！")
