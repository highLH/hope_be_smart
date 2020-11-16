#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback
import sqlite3

import libserver
import libdb as db
import libprintf as lp


if len(sys.argv) != 7:
    print("usage:", sys.argv[0], "<current-ip> <port> <next-ip> <port> <last-ip> <port>")
    sys.exit(1)

###获取创建基础表所需参数
current_ip, current_port = sys.argv[1], int(sys.argv[2])
next_ip, next_port = sys.argv[3], int(sys.argv[4])
last_ip, last_port = sys.argv[5], int(sys.argv[6])
local_info=[current_ip, current_port, next_ip, next_port, last_ip, last_port]

db.current_server = current_ip
###

###检查基础数据库
current_name = current_ip.replace('.','_')
local_db_name = db.db_path+'local_addr_'+current_name+'.db'
lp.DEBUG(local_db_name)
if not(db.check_db_not_exist(local_db_name)):
    lp.STATE("local db does not exist")
    db.build_local_addr_port_db(local_db_name, local_info)
else:
    lp.SUCC("local db exists")

route_db_name = db.db_path+'route_'+current_name+'.db'
if not(db.check_db_not_exist(route_db_name)):
    lp.STATE("route db does not exist")
    db.build_route_db(route_db_name)
    db.insert_route_db(route_db_name)
else:
    lp.SUCC("route db exists")
###

sel = selectors.DefaultSelector()

###连接、生成message、注册selector
def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print("accepted connection from", addr)
    conn.setblocking(False)
    message = libserver.Message(sel, conn, addr)
    sel.register(conn, selectors.EVENT_READ, data=message)

###设置server socket
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Avoid bind() exception: OSError: [Errno 48] Address already in use
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind((current_ip, current_port))
lsock.listen()
print("listening on", (current_ip, current_port))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            lp.DEBUG(key.data)
            #key.data：Message object的session ID e.g.<libserver.Message object at 0x7f5ae1da3a90> 
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                message = key.data
                try:
                    message.process_events(mask)
                except Exception:
                    print(
                        "main: error: exception for",
                        f"{message.addr}:\n{traceback.format_exc()}",
                    )
                    message.close()
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")

finally:
    sel.close()