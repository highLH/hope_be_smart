#!/usr/bin/env python3
#coding=utf-8

import socket

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))    # HOST为空则可接收所有可用的IPv4连接
                            # PORT：1 - 65535
                            # HOST使用域名时根据名字解析过程会有不同的结果 i.e. 推荐numeric addr
    s.listen()  # (v3.5)optional arg: backlog -> 可监听的最多连接数
                # max_val取决于系统 -> e.g. /proc/sys/net/core/somaxconn
    conn, addr = s.accept() # 返回1.new socket(connection) 2.client addr
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)