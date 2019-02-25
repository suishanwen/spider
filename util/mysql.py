import pymysql
# from pymysqlpool import ConectionPool
import uuid


def get_connect():
    # conn = pymysql.connect(
    #     host="10.10.201.22", passwd="wU$S#8Hk@tC9coCr",
    #     user="hcuser", port=3306, db="hcinfo", charset="utf8"
    # )
    conn = pymysql.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        passwd="q1212456",
        db="vh",
        charset="utf8"
    )
    conn.autocommit(True)
    return conn


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


def insert_html_record(pk_artcl, pk_org, title, src_url, path, pub_time):
    if not check_exist(title, src_url):
        sql = [
            "insert into tb_artcl_copy1 (pk_artcl, pk_org, title, src_url, contfile_fullpath, pub_time) values ('%s', '%s' ,'%s','%s','%s','%s')"
            % (pk_artcl, pk_org, title, src_url, path, pub_time)]
        execute_sql(sql[0])


def insert_mapping(pk_artcl_file, pk_artcl, file_type_name, file_name, file_path):
    if not check_mapping_exist(file_name, file_path):
        sql = [
            "insert into mapping_artcl_file_copy1 (pk_artcl_file, pk_artcl, file_type_name, file_name, file_path) values('"
            + pk_artcl_file + "','" + pk_artcl + "','" + file_type_name + "','" + file_name + "','" + file_path + "')"]
        execute_sql(sql[0])


def select_record():
    sql = ['select * from tb_artcl_copy1 order by pk_artcl']
    conn = get_connect()
    cur = conn.cursor()
    cur.execute(sql[0])
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result


def check_exist(title, src_url):
    sql = [
        "select count(1) from tb_artcl_copy1 where title = '%s' and src_url='%s'" % (title, src_url)]
    conn = get_connect()
    cur = conn.cursor()
    cur.execute(sql[0])
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result[0][0] > 0


def check_mapping_exist(file_name, file_path):
    sql = [
        "select count(1) from mapping_artcl_file_copy1 where file_name = '%s' and file_path='%s'" % (
            file_name, file_path)]
    conn = get_connect()
    cur = conn.cursor()
    cur.execute(sql[0])
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result[0][0] > 0


if __name__ == '__main__':
    print(check_exist('2015-11-17_新资源食品管理办法',
                      'http://www.beijing.gov.cn/zfxxgk/110088/flfg22/2015-11/17/content_637891.shtml'))
