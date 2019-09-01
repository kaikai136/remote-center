#！/usr/bin/python
# -*- config:utf-8 -*-
# project: 远程驾驶控制中心
# user：kaikai136
# Author: 开开
# email: jienkai136@sina.com
# createtime: 2019/5/1622:04
import json
import os
import socketserver

import threading

import datetime

import mysql_base
import rides_base

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
RIDES_SERVER = os.getenv('RIDES_SERVER', "192.168.245.8")
RIDES_PORT = os.getenv('RIDES_PORT', '6379')
DB = os.getenv('DB',0)
RIDES_PASSWORD = os.getenv('RIDES_PASSWORD','')


SOCKET_SERVER = os.getenv('SOCKET_SERVER', "0.0.0.0")
SOCKET_PORT = os.getenv('SOCKET_PORT', 8712)
SOCKETWEB_PORT = os.getenv('SOCKETWEB_PORT', 6089)
ADDRESS = (SOCKET_SERVER, int(SOCKET_PORT))  # 绑定地址
g_conndict_pool = {} # 字典链接对应关系连接池
mysql = mysql_base.getDB()
rds = rides_base.REDIS(host=RIDES_SERVER, port=RIDES_PORT, password=RIDES_PASSWORD, db=DB)
class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def setup(self):
        self.request.sendall("连接服务器请输入密钥信息!".encode(encoding='utf8'))
    def handle(self):
        while True:
            try:
                bytes = self.request.recv(1024)
                data = bytes.decode(encoding="utf8")
                try:
                    _,client_address =  self.client_address
                    data_json = eval(data)
                    try:
                        g_conndict_pool[data_json['carID']] = self.request
                        sql = 'select app_key from appinfo where deviceId={}'.format(data_json['carID'])
                        result = mysql.getOne(sql)
                    except Exception as e:
                        g_conndict_pool[data_json['BenchID']] = self.request
                        sql = 'select app_key from appinfo where deviceId=%s' % data_json['BenchID']
                        result = mysql.getOne(sql)
                    if data_json['key'] == result['app_key']:
                        try: # 台架
                            reg_plat = {"type": "2", "online": 1, "deviceid": str(data_json['BenchID'])}
                            rds.rpush('message',reg_plat)
                            sql = 'update platforminfo set platformIp="{}",parsePort="{}",online={},create_at="{}" where platformId={};'.format(data_json['Platform_ip'],data_json['Port'],1,datetime.datetime.now(),data_json['BenchID'])
                            mysql.update(sql)
                        except Exception as e:  # 车
                            reg_car = {"type": "1", "online": 1, "deviceid": str(data_json['carID'])}
                            rds.rpush('message', reg_car)
                            sql = 'update carinfo set online={},carIp="{}",create_at="{}" where carId={};'.format(1,data_json['ip'],datetime.datetime.now(),data_json['carID'])
                            mysql.update(sql)
                    print('注册成功')
                    self.request.sendall('Success\0'.encode(encoding='utf8'))
                except Exception as e:
                    self.request.sendall('数据格式不正常，重新发送'.encode(encoding='utf8'))
                    print("客户端消息：", data)
            except:  # 意外掉线
                self.remove()
                break

    def finish(self):
        print("清除了这个客户端。")

    def remove(self):
        print("有一个客户端掉线了。")
        socker_key = list(g_conndict_pool.keys())[list(g_conndict_pool.values()).index(self.request)]
        try: # 台架
            type = socker_key[:1]
            if int(type) == 2:
                reg_plat = {"type": '1', "online": 0, "deviceid": socker_key}
                rds.rpush('message', reg_plat)
            else:
                reg_car = {"type": '2', "online": 0, "deviceid": socker_key}
                rds.rpush('message', reg_car)
            sql_plat = 'update platforminfo set online={},create_at="{}" where platformId={};'.format(0,datetime.datetime.now(), socker_key)
            mysql.update(sql_plat)
            sql_carinfo = 'update carinfo set online={},create_at="{}" where carId={};'.format(0,datetime.datetime.now(),socker_key)
            mysql.update(sql_carinfo)
        except Exception as e: # 车
            ...
        del g_conndict_pool[socker_key]


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    ...


if __name__ == '__main__':
    server = ThreadedTCPServer(ADDRESS, ThreadedTCPRequestHandler)
    # 新开一个线程运行服务端
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # 主线程逻辑
    while True:
        cmd = input("""--------------------------
输入1:查看当前在线人数
输入2:给指定客户端发送消息
输入3:关闭服务端
""")

        #         print("""--------------------------
# # 输入1:查看当前在线人数
# # 输入2:给指定客户端发送消息
# # 输入3:关闭服务端
# """)
        '''
        import socket
        # 1.创建套接字
        tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 2.绑定端口
        addr = (SOCKET_SERVER, int(SOCKETWEB_PORT))
        tcp_server_socket.bind(addr)
        # 3.监听链接
        tcp_server_socket.listen(1024)
        client_socket, client_addr = tcp_server_socket.accept()
        # 5.接收对方发送的数据
        recv_data = client_socket.recv(1024)
        cmd = recv_data.decode("utf-8")
        print("接收到的数据：%s" % recv_data.decode("utf-8"))

        if cmd == '1':
            print("--------------------------")
            print("当前在线人数：", len(g_conndict_pool))
            client_socket.send(str(len(g_conndict_pool)).encode("utf-8"))
            client_socket.close()
            tcp_server_socket.close()
        elif len(cmd.split(",",1))==2:
            print("--------------------------")
            index, response = cmd.split(",",1)
            try:
                print('发送中。。。。')
                try:
                    send_data = eval(response)
                    jresp = json.dumps(send_data)
                    g_conndict_pool[index].sendall(jresp.encode(encoding='utf8'))
                except Exception as e:
                    ...
                client_socket.send("操作成功".encode("utf-8"))
                client_socket.close()
                tcp_server_socket.close()
            except Exception as e:
                print('发送失败')
                client_socket.send("失败成功".encode("utf-8"))
                client_socket.close()
                tcp_server_socket.close()
        elif cmd == '3':
            server.shutdown()
            server.server_close()
            exit()

'''


        if cmd == '1':
            print("--------------------------")
            print("当前在线人数：", len(g_conndict_pool))
        elif cmd == '2':
            print("--------------------------")
            # index, msg = input("请输入“索引,消息”的形式：").split(",")
            # g_conn_pool[int(index)].sendall(msg.encode(encoding='utf8'))
        elif cmd == '3':
            server.shutdown()
            server.server_close()
            exit()