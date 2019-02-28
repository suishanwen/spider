import sys
import requests
import os, stat, time
from util.logger import Logger

# 屏蔽warning信息
requests.packages.urllib3.disable_warnings()


def py_download(url, file_path):
    # 第一次请求是为了得到文件总大小
    r1 = requests.get(url, stream=True, verify=False)
    total_size = int(r1.headers['Content-Length'])
    # 这重要了，先看看本地文件下载了多少
    if os.path.exists(file_path):
        fileStats = os.stat(file_path)  # 获取文件/目录的状态
        fileInfo = {
            'Size': fileStats[stat.ST_SIZE],  # 获取文件大小
            'LastModified': fileStats[stat.ST_MTIME],  # 获取文件最后修改时间
            'CreationTime': fileStats[stat.ST_CTIME],  # 获取文件创建时间
            'Mode': fileStats[stat.ST_MODE]  # 获取文件的模式
        }
        temp_size = fileInfo['Size']  # 本地已经下载的文件大小
        GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
        modified_file = fileInfo['LastModified']
        modified_url = int(time.mktime(time.strptime(r1.headers['Last-Modified'], GMT_FORMAT))) + 8 * 3600
        if modified_url >= modified_file or temp_size > total_size:
            os.remove(file_path)
            Logger.info("重新下载:url:%s local:%s" % (time.ctime(modified_url), time.ctime(modified_file)))
            temp_size = 0
    else:
        temp_size = 0
    if temp_size == total_size:
        Logger.info(file_path + "已存在")
        return True
    else:
        # 显示一下下载了多少
        Logger.info("开始下载: %s, 总共：%d ,当前：%d" % (url, total_size, temp_size))
    # 核心部分，这个是请求下载时，从本地文件已经下载过的后面下载
    headers = {'Range': 'bytes=%d-' % temp_size}
    # 重新请求网址，加入新的请求头的
    r = requests.get(url, stream=True, verify=False, headers=headers)
    # r = requests.get(url, stream=True, verify=False)
    # 下面写入文件也要注意，看到"ab"了吗？
    # "ab"表示追加形式写入文件
    with open(file_path, "ab") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                temp_size += len(chunk)
                f.write(chunk)
                f.flush()
                ###这是下载实现进度显示####
                done = int(50 * temp_size / total_size)
                sys.stdout.write("\r[%s%s] %d%%" % ('█' * done, ' ' * (50 - done), 100 * temp_size / total_size))
                sys.stdout.flush()
    if total_size == temp_size:
        Logger.info(" %s 下载完成, 总共：%d ,当前：%d" % (url, total_size, temp_size))
        print()  # 避免上面\r 回车符
        return True
    return False


def simple_download(url, file_path):
    r = requests.get(url, stream=True, verify=False)
    with open(file_path, "ab") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
