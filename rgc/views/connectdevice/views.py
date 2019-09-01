# -*- coding：utf8 -*-
# @Time : 2019/5/10 14:43 
# @Author : muyongzhen
# @File : views.py 

import datetime
import socket

from flask import jsonify, current_app, request
from sqlalchemy import and_

from rgc import db
from rgc.views.connectdevice import conn_info
from rgc.model.models import ConnectDevice, CarInfo, PlatformInfo
from rgc.tools.response_code import RET, error_map
from rgc.tools.utils import is_login
from rgc.tools.redis_message_order import write_redis_message_order


def conn_socket(id, conn_data):
    dest_ip = '127.0.0.1'
    dest_port = int(6089)
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 2.连接服务器
    dest_addr = (dest_ip, dest_port)
    tcp_socket.connect(dest_addr)
    # 3. 接收/发送数据
    send_data = '{},{}'.format('car_' + id, conn_data)
    tcp_socket.send(send_data.encode("utf-8"))
    # 接收服务器发送的数据
    # recv_data = tcp_socket.recv(1024)
    # print(recv_data.decode("utf-8"))
    # 4. 关闭套接字socket
    tcp_socket.close()


@conn_info.route("/connectstatusdevice/", methods=["post"])
@is_login
def conn_dstatus_device():
    carId = request.form.get("carId")
    platformId = request.form.get("platformId")
    is_conn = request.form.get("is_conn")
    try:
        if is_conn not in ["1", "0"]:
            return jsonify(code=RET.PARAMERR, msg="is_conn:" + error_map.get(RET.PARAMERR))
        if not all([carId, platformId, is_conn]):
            return jsonify(code=RET.PARAMERR, msg=error_map.get(RET.PARAMERR))
        car = CarInfo.query.filter(and_(CarInfo.carId == carId, CarInfo.online == 1)).first()
        plat = PlatformInfo.query.filter(and_(PlatformInfo.platformId == platformId, PlatformInfo.online == 1)).first()
        if not all([car, plat]):
            return jsonify(code=RET.PARAMERR, msg="车辆或架台不在线无法操作")
        conn_real = ConnectDevice.query.all()
        car_id_list = [conn.car_id for conn in conn_real]
        platform_id_list = [conn.platform_id for conn in conn_real]
        if is_conn == "1":
            # 需要连接
            if carId in car_id_list:
                return jsonify(code=RET.PARAMERR, msg="车辆 已连接请先断开")
            if platformId in platform_id_list:
                return jsonify(code=RET.PARAMERR, msg="架台 已连接请先断开")
            newconn = ConnectDevice()
            newconn.car_id = carId
            newconn.platform_id = platformId
            newconn.create_at = datetime.datetime.now()
            db.session.add(newconn)
        elif is_conn == "0":
            # 断开
            if carId not in car_id_list:
                return jsonify(code=RET.PARAMERR, msg="车辆 未连接")
            if platformId not in platform_id_list:
                return jsonify(code=RET.PARAMERR, msg="架台 未连接")
            delconn = ConnectDevice.query.filter(and_(
                ConnectDevice.platform_id == platformId,
                ConnectDevice.car_id == carId
            )).first()
            if not delconn:
                return jsonify(code=RET.PARAMERR, msg="车辆与架台 未连接")
            db.session.delete(delconn)
        db.session.commit()
    except Exception as e:
        # print(e)
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(code=RET.DBERR, msg=error_map.get(RET.DBERR))

    conn = {"carId": carId, "platformId": platformId, "is_conn": is_conn, "platformIp": plat.platformIp,
            "parsePort": int(plat.parsePort)}
    try:
        conn_socket(conn["carId"], conn)
    except Exception as e:
        # print(e)
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(code=RET.DBERR, msg='链接失败')

    # 下达命令 同步数据向数据中心
    write_redis_message_order("2", {"carId": carId, "platformId": platformId, "is_conn": is_conn,
                                    "platformIp": plat.platformIp, "parsePort": plat.parsePort})

    # 将消息放入socketio的消息队列中
    write_redis_message_order("1", {"type": "1", "deviceid": carId, "online": 1})
    write_redis_message_order("1", {"type": "2", "deviceid": platformId, "online": 1})
    return jsonify(code=RET.OK, msg=error_map.get(RET.OK))


@conn_info.route("/connectGetlist/", methods=["get"])
@is_login
def connect_get_list_request():
    """获取所有连接的详情"""
    try:
        conns = ConnectDevice.query.all()
        data_list = list()
        for conn in conns:
            car = CarInfo.query.filter(CarInfo.carId == conn.car_id).first()
            platform = PlatformInfo.query.filter(PlatformInfo.platformId == conn.platform_id).first()
            data_list.append({"carInfo": car.to_dict(), "platformInfo": platform.to_dict(),
                              "create_at": conn.create_at.strftime("%Y-%m-%d %H:%M:%S")})
        return jsonify(code=RET.OK, msg=error_map.get(RET.OK), data=data_list)
    except Exception as e:
        current_app.looger.error(e)
        return jsonify(code=RET.DBERR, msg=error_map.get(RET.DBERR))
