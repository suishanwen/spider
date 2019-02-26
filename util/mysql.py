import pymysql
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
def execute_sql(sql):
    if sql:
        try:
            conn = get_connect()
            cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
            cur.execute(sql)
            cur.close()
            conn.close()
        except pymysql.DatabaseError:
            print("insert error")


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


# 获取pk_org
def get_pk_org(org_name):
    sql = ["select pk_org from mdm_orginazation where org_name = '%s'" % (org_name)]
    conn = get_connect()
    cur = conn.cursor()
    cur.execute(sql[0])
    result = cur.fetchall()
    cur.close()
    conn.close()
    if len(result) == 0:
        Logger.error("未找到Org:%s", org_name)
        exit()
    return result[0][0]


# 获取pk_channel
def get_pk_channel(pk_org, web_site_url):
    sql = [
        "select pk_channel from mdm_webchannel where pk_org = '%s' and web_site_url='%s'" % (
            pk_org, web_site_url)]
    conn = get_connect()
    cur = conn.cursor()
    cur.execute(sql[0])
    result = cur.fetchall()
    cur.close()
    conn.close()
    if len(result) == 0:
        Logger.error("未找到Channel,pk_org:%s ,web_site_url:%s" % (pk_org, web_site_url))
        exit()
    return result[0][0]
