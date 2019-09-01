# ！/usr/bin/python
# -*- config:utf-8 -*-
# project: 远程驾驶控制中心
# user：kaikai136
# Author: 开开
# email: jienkai136@sina.com
# createtime: 2019/5/1622:04
import json
import os
import socket
import socketserver

import threading

import datetime
import time

import mysql_base
import rides_base

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
RIDES_SERVER = os.getenv('RIDES_SERVER', "192.168.245.8")
RIDES_PORT = os.getenv('RIDES_PORT', '6379')
DB = os.getenv('DB', 0)
RIDES_PASSWORD = os.getenv('RIDES_PASSWORD', '')

SOCKET_SERVER = os.getenv('SOCKET_SERVER', "0.0.0.0")
SOCKET_PORT = os.getenv('SOCKET_PORT', 8712)
SOCKETWEB_PORT = os.getenv('SOCKETWEB_PORT', 6089)
ADDRESS = (SOCKET_SERVER, int(SOCKET_PORT))  # 绑定地址
g_conndict_pool = {}  # 字典链接对应关系连接池
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
                if not data:
                    print('data', data, 'end')
                    try:
                        self.remove()
                    except Exception as e:
                        print('error_7', e)
                    break
                if not isinstance(data, str):
                    try:
                        self.request.send('数据格式不正常，重新发送'.encode(encoding='utf8'))
                        print("客户端消息：", data)
                    except Exception as e:
                        print('error_1', e)
                        try:
                            self.remove()
                        except Exception as e:
                            print('error_7', e)
                        break
                    continue
                else:
                    try:
                        data_json = json.loads(data, encoding='utf-8')
                    except Exception as e:
                        try:
                            self.request.send('数据格式不正常，重新发送'.encode(encoding='utf8'))
                            print("客户端消息：", data)
                        except Exception as e:
                            print('error_2', e)
                            try:
                                self.remove()
                            except Exception as e:
                                print('error_7', e)
                            break
                        continue
                try:
                    _, client_address = self.client_address
                    # data_json = eval(data)
                    try:
                        sql = 'select app_secret, type, deviceId from appinfo where app_key="%s"' % data_json['key']
                        result = mysql.getOne(sql)
                        if result['type'] == '1':
                            pool_key = 'car_' + result['deviceId']
                        elif result['type'] == '2':
                            pool_key = 'pla_' + result['deviceId']
                        else:
                            raise Exception('type不是"1"或者"2"')
                        g_conndict_pool[pool_key] = self.request
                    except Exception as e:
                        print('error_3', e)
                    print(result['type'])
                    if data_json['secret'] == result['app_secret']:
                        print(result['type'], type(result['type']))
                        if result['type'] == '2':
                            print('plat')
                            reg_plat = {"type": "2", "online": 1, "deviceid": str(result['deviceId'])}
                            reg_plat = json.dumps(reg_plat)
                            rds.rpush('message', reg_plat)
                            sql = 'update platforminfo set platformIp="{}",parsePort="{}",online={},create_at="{}" where platformId={};'.format(
                                data_json['plat_ip'], data_json['plat_port'], 1, datetime.datetime.now(),
                                result['deviceId'])
                            mysql.update(sql)
                        elif result['type'] == '1':
                            print('car')
                            reg_car = {"type": "1", "online": 1, "deviceid": str(result['deviceId'])}
                            reg_car = json.dumps(reg_car)
                            rds.rpush('message', reg_car)
                            sql = 'update carinfo set online={},carIp="{}",create_at="{}" where carId={};'.format(1, data_json['ip'], datetime.datetime.now(), result['deviceId'])
                            mysql.update(sql)
                    print('注册成功')
                    self.request.sendall('Success\0'.encode(encoding='utf8'))
                except Exception as e:
                    print('error_5', e)
                    try:
                        self.request.sendall('数据格式不正常，重新发送'.encode(encoding='utf8'))
                        print("客户端消息：", data)
                    except Exception as e:
                        print('error_4', e)
            except Exception as e:  # 意外掉线
                print('error_6', e)
                try:
                    self.remove()
                except Exception as e:
                    print('error_7', e)
                break

    def finish(self):
        print("清除了这个客户端。")

    def remove(self):
        print("有一个客户端掉线了。")
        socker_key = list(g_conndict_pool.keys())[list(g_conndict_pool.values()).index(self.request)]
        try:
            type = socker_key[0:4]
            if type == 'car_':
                reg_car = {"type": '1', "online": 0, "deviceid": socker_key[4:]}
                reg_car = json.dumps(reg_car)
                try:
                    print('车辆下线')
                    rds.rpush('message', reg_car)
                except Exception as e:
                    print('eeee', e)

                sql_plat = 'update platforminfo set online={},create_at="{}" where platformId={};'.format(0,
                                                                                                          datetime.datetime.now(),
                                                                                                          socker_key[
                                                                                                          4:])
                mysql.update(sql_plat)
            else:
                reg_plat = {"type": '2', "online": 0, "deviceid": socker_key[4:]}
                reg_plat = json.dumps(reg_plat)
                try:
                    print('台架下线')
                    rds.rpush('message', reg_plat)
                except Exception as e:
                    print('eeee', e)

                sql_carinfo = 'update carinfo set online={},create_at="{}" where carId={};'.format(0,
                                                                                                   datetime.datetime.now(),
                                                                                                   socker_key[4:])
                mysql.update(sql_carinfo)
        except Exception as e:
            print('error_7', e)

        del g_conndict_pool[socker_key]


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        socketserver.TCPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate=True)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, 10)
        self.socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, 6)
        self.socket.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, 3)


def heart_test_remove(value):
    print("有一个客户端掉线了。")
    socker_key = list(g_conndict_pool.keys())[list(g_conndict_pool.values()).index(value)]
    try:
        type = socker_key[0:4]
        if type == 'car_':
            reg_car = {"type": '1', "online": 0, "deviceid": socker_key[4:]}
            reg_car = json.dumps(reg_car)
            try:
                print('车辆下线')
                rds.rpush('message', reg_car)
            except Exception as e:
                print('eeee', e)

            sql_plat = 'update platforminfo set online={},create_at="{}" where platformId={};'.format(0,
                                                                                                      datetime.datetime.now(),
                                                                                                      socker_key[
                                                                                                      4:])
            mysql.update(sql_plat)
        else:
            reg_plat = {"type": '2', "online": 0, "deviceid": socker_key[4:]}
            reg_plat = json.dumps(reg_plat)
            try:
                print('台架下线')
                rds.rpush('message', reg_plat)
            except Exception as e:
                print('eeee', e)

            sql_carinfo = 'update carinfo set online={},create_at="{}" where carId={};'.format(0,
                                                                                               datetime.datetime.now(),
                                                                                               socker_key[4:])
            mysql.update(sql_carinfo)
    except Exception as e:
        print('error_7', e)

    del g_conndict_pool[socker_key]


def heart_test():
    while True:
        socket_list = g_conndict_pool.keys()
        for i in socket_list:
            try:
                i.send("test".encode(encoding='utf8'))
            except Exception as e:
                print('error_1', e)
                try:
                    heart_test_remove(i)
                except Exception as e:
                    print('error_7', e)
                break
        print(g_conndict_pool)
        time.sleep(3)


def main():
    server = ThreadedTCPServer(ADDRESS, ThreadedTCPRequestHandler)
    # 新开一个线程运行服务端
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    heart_test_thread = threading.Thread(target=heart_test)
    heart_test_thread.daemon = True
    heart_test_thread.start()

    # 主线程逻辑
    while True:
        print("""--------------------------
    # 输入1:查看当前在线人数
    # 输入2:给指定客户端发送消息
    # 输入3:关闭服务端
    """)
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
        elif len(cmd.split(",", 1)) == 2:
            print("--------------------------")
            index, response = cmd.split(",", 1)
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


if __name__ == '__main__':
    main()
