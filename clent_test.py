# ！/usr/bin/python
# -*- config:utf-8 -*-
# project: 远程驾驶控制中心
# user：kaikai136
# Author: 开开
# email: jienkai136@sina.com
# createtime: 2019/5/1622:04


# import socket  # 导入 socket 模块
# import time
# s = socket.socket()  # 创建 socket 对象
# s.connect(('127.0.0.1', 8712))
# print(s.recv(1024).decode(encoding='utf8'))
# send_data = {'time': time.time(), "key": "9f69d16c95824a62", "carID": "1"}
# send_data = str(send_data)
# s.send(send_data.encode('utf8'))
# print(s.recv(1024).decode(encoding='utf8'))
# input("")

# ！/usr/bin/python
# -*- config:utf-8 -*-
# project: 服务
# user：kaikai136
# Author: 开开
# email: jienkai136@sina.com
# createtime: 2019/4/415:15

import socket
import time

dest_ip = '127.0.0.1'
dest_port = 8712


def socket_connect(host, port):
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        socket_client.connect((host, port))
    except:
        pass
    return socket_client


tcp_socket = socket_connect(dest_ip, dest_port)

send_data = {"Platform_ip": "192.168.215.248", "Port": "8712", "key": "0f64b593ed83ac61", "BenchID": "1001"}
#         time.sleep(0.1)
send_data = str(send_data)
# tcp_socket.send(send_data)
tcp_socket.send(send_data.encode("utf-8"))


def main():
    try:
        global tcp_socket
        # 测试数据
        # 接收服务器发送的数据
        recv_data = tcp_socket.recv(2048)
        print(recv_data.decode("utf-8"))
        # send_data = input('输入信息：')
        # tcp_socket.send(send_data.encode("utf-8"))
        # 4. 关闭套接字socket
        # tcp_socket.close()
    except socket.error:
        time.sleep(1)
        # 服务端断开链接等待服务端启动重新链接
        tcp_socket = socket_connect(dest_ip, dest_port)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    while True:
        main()
