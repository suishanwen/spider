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


def insert_html_record(pk_artcl, title, src_url, path, pub_time):
    sql = ["insert into tb_artcl_copy1 (pk_artcl, pk_org, title, src_url, contfile_fullpath, pub_time) values ('" +
                pk_artcl + "', '国家卫生健康委员会' ,'" + title + "','" + src_url + "','" + path + "','" + pub_time + "')"]
    execute_sql(sql[0])


def insert_mapping(pk_artcl_file, pk_artcl, file_type_name, file_name, file_path):
    sql = ["insert into mapping_artcl_file_copy1 (pk_artcl_file, pk_artcl, file_type_name, file_name, file_path) values('"
           + pk_artcl_file + "','" + pk_artcl + "','" + file_type_name + "','" + file_name+"','" + file_path + "')"]
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


if __name__ == '__main__':
    select_record()
