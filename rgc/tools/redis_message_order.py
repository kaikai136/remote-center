# -*- coding：utf8 -*-
# @Time : 2019/5/23 11:18 
# @Author : muyongzhen
# @File : redis_message_order.py
import json

from rgc import redis_store

"""
向前端传输的数据格式 {"type": "1", "online": 1, "deviceid": "001"}
小车或架台异常掉线  需要传入当前设备的下线状态，和掉线前对应连接设备的上线状态（如何当前设备是连接状态时意外下线）
像数据中心传的数据格式 {"carId": "002", "platformId": "001", "is_conn": 0, "platformIp": "127.0.0.1", "parsePort": "8080"}}
"""


def write_redis_message_order(type, msg):
    msg = json.dumps(msg)
    if type == "1":
        """写入socketio的数据"""
        redis_store.rpush("message", msg)
    elif type == "2":
        """写入向数据中心同步的数据"""
        redis_store.rpush("order", msg)


def read_redis_message_order(type):
    msg = ""
    if type == "1":
        msg = redis_store.lpop("message")
    elif type == "2":
        msg = redis_store.lpop("order")
    if msg:
        # msg = eval(msg)
        msg = json.loads(msg)
    return msg
