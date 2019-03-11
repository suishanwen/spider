import requests
from util.download import py_download, simple_download
from util.file import validate_title

# ->
# /home/hia/spider/file/国家卫生健康委员会/委厅文件/国家卫生计生委关于印发医疗机构临床检验项目目录_2013年版/20130807163248809.xlsx
# 开始第8次断点下载！
# [2019-03-07 20:42:55] WARNING [get_ext: processor.py, 151]
# http://www.nhc.gov.cn/ewebeditor/uploadfile/2013/08/20130807163248809.xlsx [异常]断点下载失败 'content-length'！

# # 重新请求网址，加入新的请求头的
# # url = "http://www.nhc.gov.cn/ewebeditor/uploadfile/2016/07/20160704105324687.jpg"
# url = "http://www.nhc.gov.cn/zhjcj/s9141/201002/830e8d08985346d7ac8df0c7d7ac2acb/files/20c49ee75d0b4748a69a022f039f86f6.xls"
# url = 'http://www.nhfpc.gov.cn/cmsresources/mohbgt/cmsrsdocument/doc14811.pdf'
# url = 'http://www.moh.gov.cn/open/web_edit_file/20080310142354.doc'
# url = "http://www.nhc.gov.cn/ewebeditor/uploadfile/2013/08/20130807163248809.xlsx"
# url = "http://www.nhfpc.gov.cn/cmsresources/mohbgt/cmsrsdocument/doc14812.pdf"
# path = "./file/%s" % url[url.rfind('/') + 1:len(url)]
# state, code = py_download(url, path)
# print(state)
# print(code)
# state = simple_download(url, path))
# session = requests.session()
# r = session.get(url)
# file = open(path, "wb")
# file.write(r.content)
# file.flush()
# file.close()
# r1 = requests.get(url)
# with open(path, "ab") as f:
#     for chunk in r.iter_content(chunk_size=1024):
#         if chunk:
#             f.write(chunk)
#             f.flush()
# print(r.status_code)
# print(r1.status_code)
# print(code)
# str = "关于发布2009年11-12月份获批消毒和涉水卫生安全产品的通告（卫通〔2010〕3号）"
# print(validate_title(str))
# /home/hia/spider/file/国家卫生健康委员会/年报/
# http://www.moh.gov.cn/cmsresources/mohyzs/cmsrsdocument/doc14934.doc
# /home/hia/spider/file/国家卫生健康委员会/季报/关于2012年第一季度全国血液采集情况的通报/doc14934.doc
# HTTPConnectionPool(host='www.moh.gov.cn', port=80):
# Max retries exceeded with url: /cmsresources/mohyzs/cmsrsdocument/doc14934.doc
# (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7f39d8aa0ac8>: Failed to establish a new connection: [Errno -2] Name or service not known',))！
#
# from concurrent.futures import ThreadPoolExecutor, as_completed
# import time
#
#
# def aaa(a):
#     print(a)
#     time.sleep(2)
#
#
# task_list = []
# with ThreadPoolExecutor(2) as executor:
#     task_list.append(executor.submit(aaa, "1"))
#     task_list.append(executor.submit(aaa, "2"))
#     task_list.append(executor.submit(aaa, "3"))
#     for task in as_completed(task_list):
#         print("线程[%s]执行完成" % str(task))

# domain = "http://www.nhc.gov.cn"
# url = "http://www.nhc.gov.cn/123"
# print(url in domain)
# print(domain in url)
# print(url[0:url.find("/", 8)])
# headers = {
#     'Accept': 'application/json, text/javascript, */*; q=0.01',
#     'Accept-Encoding': 'gzip, deflate',
#     'Accept-Language': 'zh-CN,zh;q=0.8',
#     'Connection': 'keep-alive',
#     'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
#     'Host': 'login.189.cn',
#     'Origin': 'https://login.189.cn',
#     'Referer': 'https://login.189.cn/web/login',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
#     'X-Requested-With': 'XMLHttpRequest'
# }
# url = "http://www.moh.gov.cn"
# r = requests.get(url, headers=headers)

# py_download()
# print(r)
# attachment_uri = "/ewebeditor/uploadfile/2013/04/20130403171413251.JPG"
# relate_img = attachment_uri[0:attachment_uri.rfind(".")] + "_s" + "." + "JPG"
# print(relate_img)
