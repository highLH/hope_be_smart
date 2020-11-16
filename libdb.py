#coding=utf-8

import sqlite3
import libprintf as lp

db_path = './data/'
current_server = None


######## 建本地地址-端口表
def build_local_addr_port_db(db_name, info):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    table = db_name[len(db_path):(len(db_name)-3)]
    lp.DEBUG(table)
    cur.execute(
        "CREATE TABLE "+table+" "+
        "(   \
            object varchar(20) primary key, \
            address varchar(20),    \
            port int    \
        )")
    #sqlite3中插入数据只能一条一条写入（一次多条是非标准的SQL语句，故sqlite3中不支持）
    lp.DEBUG(str(info[0]))
    cur.execute(
        "INSERT INTO "+table+" "
        +"SELECT 'self' AS 'object', '"+str(info[0])+"' AS 'address', "+str(info[1])+" AS 'port' "
        +"UNION SELECT 'next_hop', '"+str(info[2])+"', "+str(info[3])+" " 
        +"UNION SELECT 'last_hop', '"+str(info[4])+"', "+str(info[5])
    )
    if cur.rowcount == 3:
        lp.SUCC("Successfully build a static table for local_db")
    cur.close()
    conn.commit()
    conn.close()

######## 建路由表
def build_route_db(db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    table = db_name[len(db_path):(len(db_name)-3)]
    lp.DEBUG(table)
    cur.execute(
        "CREATE TABLE "+table+" "
        +"( \
            dest varchar(20) primary key,   \
            cost int,   \
            next_ip varchar(20),    \
            next_port int   \
        )")
    lp.SUCC("Successfully build a static table for route_info")
    cur.close()
    conn.commit()
    conn.close()

######## 在路由表中插值
def insert_route_db(db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    table = db_name[len(db_path):(len(db_name)-3)]
    if table == 'route_192_168_1_12':
        lp.DEBUG("Look up route_192_168_1_12 ...")
        cur.execute(
            "INSERT INTO "+table+" "
            +"SELECT '192.168.1.12' AS 'dest', 12 AS 'cost', NULL AS 'address', 0 AS 'port' "
            +"UNION SELECT '192.168.2.13', 12, '192.168.2.13', 35567 " 
            +"UNION SELECT '10.112.229.12', 12, '192.168.2.13', 35567"
        )
    elif table == 'route_192_168_2_13':
        cur.execute(
            "INSERT INTO "+table+" "
            +"SELECT '192.168.2.13' AS 'dest', 12 AS 'cost', NULL AS 'address', 0 AS 'port' "
            +"UNION SELECT '192.168.1.12', 12, '192.168.1.12', 34456 " 
            +"UNION SELECT '10.112.229.12', 12, '10.112.229.12', 36678"
        )
    elif table == 'route_10_112_229_12':
        cur.execute(
            "INSERT INTO "+table+" "
            +"SELECT '10.112.229.12' AS 'dest', 12 AS 'cost', NULL AS 'address', 0 AS 'port' "
            +"UNION SELECT '192.168.2.13', 12, '192.168.2.13', 35567 " 
            +"UNION SELECT '192.168.2.13', 12, '192.168.2.13', 35567"
        )
    else:
        lp.ERR("Failed to insert items")
    if cur.rowcount == 3:
        lp.SUCC("Successfully build a static table for local_db")
    cur.close()
    conn.commit()
    conn.close()


#######检查表是否存在
def check_db_not_exist(db_name):
    return "SELECT count(*) FROM sqlite_master  \
        WHERE type='table' AND name='%s'" %db_name

#######查route表中的下一项
def check_route_next(dest_ip):
    current_name = current_server.replace('.','_')
    db_name = db_path+'route_'+current_name+'.db'
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    table = db_name[len(db_path):(len(db_name)-3)]
    lp.DEBUG(dest_ip)
    cur.execute(
        "SELECT next_ip, next_port FROM "+table+" WHERE dest=?" , (str(dest_ip),))
    result = cur.fetchall()
    lp.DEBUG(result)

    return result
    



