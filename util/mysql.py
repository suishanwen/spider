import pymysql
import time
import uuid
from util.yaml import yaml_read
from conf.config import Const
from util.logger import Logger


# 获取数据库连接
def get_connect():
    database = yaml_read(Const.DB_YAML, ["database"])
    conn = pymysql.connect(
        host=database["host"], user=database["user"], passwd=database["passwd"],
        port=database["port"], db=database["db"], charset=database["charset"]
    )
    conn.autocommit(True)
    return conn


# 执行sql
def execute_sql(sql, count=1):
    if sql:
        try:
            conn = get_connect()
            cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
            cur.execute(sql)
            cur.close()
            conn.close()
            return True
        except pymysql.DatabaseError as e:
            Logger.info("第%d次执行sql失败！%s" % (count, str(e)))
            if count <= 3:
                count += 1
                time.sleep(1)
                return execute_sql(sql, count)
            return False


# 插入html主记录
def insert_html_record(pk_artcl, pk_org, pk_channel, title, src_url, path, pub_time):
    if not check_exist(title, src_url):
        sql = [
            "insert into tb_artcl (pk_artcl, pk_org,pk_channel, title, src_url, contfile_fullpath, pub_time) values ('%s', '%s' ,'%s','%s','%s','%s','%s')"
            % (pk_artcl, pk_org, pk_channel, title, src_url, path, pub_time)]
        execute_sql(sql[0])


# 插入html附件记录
def insert_mapping(pk_artcl_file, pk_artcl, file_type_name, file_name, file_path):
    if not check_mapping_exist(file_name, file_path):
        sql = [
            "insert into mapping_artcl_file (pk_artcl_file, pk_artcl, file_type_name, file_name, file_path) values ('%s', '%s' ,'%s','%s','%s')"
            % (pk_artcl_file, pk_artcl, file_type_name, file_name, file_path)]
        execute_sql(sql[0])


# 插入爬取失败记录
def set_toretry_task(pk_task, pk_webchannel, src_url, title, pub_time, errmsg):
    if len(errmsg) > 5000:
        errmsg = errmsg[0:5000]
    if not check_toretry_task_exist(pk_webchannel, src_url):
        Logger.warning("插入重试任务 %s！" % title)
        sql = [
            "insert into tb_toretry_task (pk_task, pk_webchannel, src_url, title, pub_time, sub_channel_name,errmsg,"
            "total_times) values ('%s', '%s' ,'%s','%s', '%s' ,'%s',%d)"
            % (pk_task, pk_webchannel, src_url, title, pub_time, errmsg, 0)]
    else:
        Logger.warning("更新重试任务 %s 尝试次数！" % title)
        sql = [
            "update tb_toretry_task set errmsg='%s',total_times=total_times+1 where pk_webchannel = '%s' and src_url ='%s'"
            % (errmsg, pk_webchannel, src_url)]
    execute_sql(sql[0])


def query_toretry_task(pk_webchannel):
    sql = [
        "select  src_url ,title ,pub_time,total_times from tb_toretry_task where pk_webchannel = '%s' and is_stop=0 " % (
            pk_webchannel)]
    conn = get_connect()
    cur = conn.cursor()
    cur.execute(sql[0])
    result = cur.fetchall()
    cur.close()
    conn.close()
    if len(result) == 0:
        Logger.info("当前channel未找到可重试的失败记录！")
    else:
        Logger.info("当前channel共找到%d条可重试的失败记录！" % len(result))
    return list(
        map(lambda data: {"src_url": data[0], "title": data[1], "pub_time": str(data[2]), "total_times": data[3]},
            result))


# 删除爬取失败记录
def delete_toretry_task(pk_webchannel, src_url, total_times):
    sql = [
        "delete from tb_toretry_task where is_stop=0 and pk_webchannel = '%s' and src_url ='%s' and total_times = %d"
        % (pk_webchannel, src_url, total_times)]
    return execute_sql(sql[0])


# 停止爬取失败记录
def stop_toretry_task(pk_webchannel):
    sql = [
        "update tb_toretry_task set is_stop=1 where pk_webchannel = '%s' and total_times>=5"
        % (pk_webchannel)]
    return execute_sql(sql[0])


# 检查html主记录 存在
def check_exist(title, src_url):
    sql = [
        "select count(1) from tb_artcl where title = '%s' and src_url='%s'" % (title, src_url)]
    conn = get_connect()
    cur = conn.cursor()
    cur.execute(sql[0])
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result[0][0] > 0


# 检查html附件记录 存在
def check_mapping_exist(file_name, file_path):
    sql = [
        "select count(1) from mapping_artcl_file where file_name = '%s' and file_path='%s'" % (
            file_name, file_path)]
    conn = get_connect()
    cur = conn.cursor()
    cur.execute(sql[0])
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result[0][0] > 0


# 检查爬取失败记录 存在
def check_toretry_task_exist(pk_webchannel, src_url):
    sql = [
        "select count(1) from tb_toretry_task where pk_webchannel = '%s' and src_url='%s'" % (
            pk_webchannel, src_url)]
    conn = get_connect()
    cur = conn.cursor()
    cur.execute(sql[0])
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result[0][0] > 0


# 获取pk_artcl
def get_pk_article(src_url, title):
    sql = ["select pk_artcl from tb_artcl where src_url = '%s' and title = '%s'" % (src_url, title)]
    conn = get_connect()
    cur = conn.cursor()
    cur.execute(sql[0])
    result = cur.fetchall()
    cur.close()
    conn.close()
    if len(result) == 0:
        return str(uuid.uuid4())
    return result[0][0]


# 获取channel
def get_channels():
    sql = [
        "select mw.pk_org,mo.org_name,mw.pk_channel,mw.channel_name,mw.web_site_url,mw.spider,mw.scrapy_page from mdm_webchannel mw"
        " inner join mdm_orginazation mo on mw.pk_org = mo.pk_org where mw.spider is not null and mw.spider <> ''"]
    conn = get_connect()
    cur = conn.cursor()
    cur.execute(sql[0])
    result = cur.fetchall()
    cur.close()
    conn.close()
    if len(result) == 0:
        Logger.warning("未找到可用channel！")
        exit()
    else:
        Logger.warning("共找到%d条可启动channel！" % len(result))
    return list(
        map(lambda data: {"pk_org": data[0], "org_name": data[1], "pk_channel": data[2], "channel_name": data[3],
                          "web_site_url": data[4], "spider": data[5], "scrapy_page": data[6]},
            result))


# 更新频道爬取页码
def update_scrapy_page(pk_channel, scrapy_page):
    sql = [
        "update mdm_webchannel set scrapy_page=%d where pk_channel = '%s'"
        % (scrapy_page, pk_channel)]
    return execute_sql(sql[0])
