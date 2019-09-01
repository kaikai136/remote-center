# -*- coding：utf8 -*-
# @Time : 2019/5/8 18:55 
# @Author : muyongzhen
# @File : views.py
import json
import time
import datetime
import uuid
import random
from flask import request, current_app, jsonify, render_template
from sqlalchemy import and_, or_
from rgc import db
import re
from rgc.model.models import CarInfo, PlatformInfo, ConnectDevice, AppInfo
from rgc.tools.utils import is_login, get_16_md5
from rgc.tools.response_code import RET, error_map
from rgc.views.car import car_info
from rgc.tools.online_type_devices import update_online_decice
from rgc.tools.redis_message_order import write_redis_message_order


@car_info.route("/getCarlist/", methods=["get"])
@is_login
def car_list_request():
    """获取车辆列表信息
       type: 2只显示在线的， 3只显示不在线的，其他显示全部的
    """
    type = request.args.get("type", "1")
    try:
        conns = ConnectDevice.query.all()
        conn_car_id_list = [conn.car_id for conn in conns]
        if type == "2":
            cars = CarInfo.query.filter(CarInfo.online == 1).all()
        elif type == "3":
            cars = CarInfo.query.filter(CarInfo.online == 0).all()
        else:
            cars = CarInfo.query.all()
        car_list = list()
        for car in cars:
            item = car.to_dict()
            if car.carId in conn_car_id_list:
                item["is_conn"] = 1
            else:
                item["is_conn"] = 0
            item["app_key"] = car.get_app_key()
            item["app_secret"] = car.get_app_secret()
            car_list.append(item)
        return jsonify(code=RET.OK, msg=error_map.get(RET.OK), data=car_list[::-1])
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(code=RET.DBERR, msg=error_map.get(RET.DBERR))


@car_info.route("/CarAdd/", methods=["POST"])
@is_login
def car_add_request():
    """新增车辆"""
    # carId = request.form.get("carId")
    carLicense = request.form.get("carLicense")

    car_last = CarInfo.query.filter().order_by(CarInfo.carId.desc()).first()
    if not car_last:
        carId = '0001'
    else:
        carId = '%04d' % (int(car_last.carId) + 1)

    if not carId:
        return jsonify(code=RET.PARAMERR, msg="车辆ID不可为空")
    if not carLicense:
        return jsonify(code=RET.PARAMERR, msg="车辆牌照不可为空")

    res_carId = re.match("^[0-9]{3,6}$", carId)
    if not res_carId:
        return jsonify(code=RET.PARAMERR, msg="车辆ID格式错误（3-6位纯数字）")

    re_carLicense = re.match('^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领A-Z]{1}[A-Z]{1}[A-Z0-9]{4}[A-Z0-9挂学警港澳]{1}$',
                             carLicense)
    if not re_carLicense:
        return jsonify(code=RET.PARAMERR, msg="车辆牌照格式错误")

    try:
        caripall = [car.carIp for car in CarInfo.query.all()]
        while True:
            carIp = "192.168.50.{}".format(random.randint(0, 256))
            if carIp not in caripall:
                break
        car1 = CarInfo.query.filter(CarInfo.carId == carId).first()
        if car1:
            return jsonify(code=RET.PARAMERR, msg="车辆ID已存在，请更换有效ID")

        car2 = CarInfo.query.filter(CarInfo.carLicense == carLicense).first()
        if car2:
            return jsonify(code=RET.PARAMERR, msg="车辆牌照已存在，请更换有效名称")
        car = CarInfo()
        car.carId = carId
        car.carIp = carIp
        car.carLicense = carLicense
        car.online = 0
        car.create_at = datetime.datetime.now()
        app = AppInfo()
        app.deviceId = carId
        app.type = "1"
        # app.app_key = get_16_md5(f"{int(time.time()*100)}{carId}")
        # app.app_secret = str(uuid.uuid4().hex)

        # app_key = get_16_md5(f"{int(time.time()*100)}{carId}")
        app_key = get_16_md5("{}{}".format(int(time.time()*100), carId))
        app.app_key = app_key
        # app.app_secret = get_16_md5(f"{app_key}{carId}")
        app.app_secret = get_16_md5("{}{}".format(app_key, carId))
        db.session.add(app)
        db.session.add(car)
        db.session.commit()
        msg = {"type": "1", "online": 0, "deviceid": carId}
        write_redis_message_order(type="1", msg=msg)
        return jsonify(code=RET.OK, msg="车辆添加成功")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(code=RET.DBERR, msg=error_map.get(RET.DBERR))


@car_info.route("/updateCarInfo/", methods=["POST"])
@is_login
def car_update_request():
    """修改车辆信息"""
    # carId = request.form.get("carId")
    id = request.form.get("id")
    carLicense = request.form.get("carLicense")

    if not id:
        return jsonify(code=RET.PARAMERR, msg="id参数不足")
    # if not carId:
    #     return jsonify(code=RET.PARAMERR, msg="车辆ID不可为空")
    if not carLicense:
        return jsonify(code=RET.PARAMERR, msg="车辆牌照不可为空")

    # res_carId = re.match("^[0-9]{3,6}$", carId)
    # if not res_carId:
    #     return jsonify(code=RET.PARAMERR, msg='车辆ID格式错误（只可包含数字）')

    re_carLicense = re.match('^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领A-Z]{1}[A-Z]{1}[A-Z0-9]{4}[A-Z0-9挂学警港澳]{1}$',
                             carLicense)
    if not re_carLicense:
        return jsonify(code=RET.PARAMERR, msg='车辆牌照格式错误')

    try:
        car3 = CarInfo.query.filter(CarInfo.id == id).first()
        if not car3:
            return jsonify(code=RET.PARAMERR, msg="车辆不存在")
        if car3.online:
            return jsonify(code=RET.PARAMERR, msg="车辆在线不能操作")

        # car1 = CarInfo.query.filter(and_(CarInfo.carId == carId, CarInfo.id != id)).first()
        # if car1:
        #     return jsonify(code=RET.PARAMERR, msg="车辆ID已存在，请更换有效ID。")
        car2 = CarInfo.query.filter(and_(CarInfo.carLicense == carLicense, CarInfo.id != id)).first()
        if car2:
            return jsonify(code=RET.PARAMERR, msg="车辆牌照已存在，请更换有效名称。")
        old_carId = car3.carId
        # app = AppInfo.query.filter(and_(AppInfo.type == "1", AppInfo.deviceId == old_carId)).first()
        # app.deviceId = carId
        # db.session.add(app)
        # car3.carId = carId
        car3.carLicense = carLicense
        db.session.add(car3)
        db.session.commit()
        write_redis_message_order(type="1", msg={"type": "1", "online": 0, "deviceid": old_carId})
        return jsonify(code=RET.OK, msg="修改保存成功")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(code=RET.DBERR, msg=error_map.get(RET.DBERR))


@car_info.route("/CarDelete/", methods=["get"])
@is_login
def car_delete_request():
    """删除车辆"""
    try:
        carId = request.args.get("carId")
        if not carId:
            return jsonify(code=RET.PARAMERR, msg=error_map.get(RET.PARAMERR))
        car = CarInfo.query.filter(CarInfo.carId == carId).first()
        if not car:
            return jsonify(code=RET.PARAMERR, msg=error_map.get(RET.PARAMERR))
        conn = ConnectDevice.query.filter(ConnectDevice.car_id == carId).first()
        if conn:
            return jsonify(code=RET.PARAMERR, msg="车辆已连接，请先断开连接")
        app = AppInfo.query.filter(and_(AppInfo.type == "1", AppInfo.deviceId == carId)).first()
        if app:
            db.session.delete(app)
        db.session.delete(car)
        db.session.commit()
        return jsonify(code=RET.OK, msg=error_map.get(RET.OK))
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(code=RET.DBERR, msg=error_map.get(RET.DBERR))


@car_info.route("/getCarinfo/", methods=["get"])
@is_login
def get_carinfo_request():
    """获取车辆详情"""
    carId = request.args.get("carId", None)
    if not carId:
        return jsonify(code=RET.PARAMERR, msg=error_map.get(RET.PARAMERR))
    try:
        car = CarInfo.query.filter(CarInfo.carId == carId).first()
        if not car:
            return jsonify(code=RET.PARAMERR, msg=error_map.get(RET.PARAMERR))
        conns = ConnectDevice.query.all()
        conn_car_id_list = [conn.car_id for conn in conns]
        data = car.to_dict()
        if carId in conn_car_id_list:
            data["is_conn"] = 1
        else:
            data["is_conn"] = 0
        data["app_key"] = car.get_app_key()
        data["app_secret"] = car.get_app_secret()
    except Exception as e:
        # print(e)
        current_app.logger.error(e)
        return jsonify(code=RET.DBERR, msg=error_map.get(RET.DBERR))
    return jsonify(code=RET.OK, msg=error_map.get(RET.OK), data=data)


# @car_info.route("/updateCaronline/", methods=["get"])
# @is_login
# def update_car_online():
#     type = request.args.get("type")
#     carId = request.args.get("carId")
#     online = request.args.get("online")
#     # name = "测试台架"
#     if not carId:
#         return jsonify(code=RET.PARAMERR, msg=error_map.get(RET.PARAMERR))
#     if not online or online not in["0", "1"]:
#         return jsonify(code=RET.PARAMERR, msg=error_map.get(RET.PARAMERR))
# try:
#     car = CarInfo.query.filter(CarInfo.carId==carId).first()
#     if not car:
#         return jsonify(code=RET.PARAMERR, msg=error_map.get(RET.PARAMERR))
#     if car.online == int(online):
#         return jsonify(code=RET.PARAMERR, msg=error_map.get(RET.PARAMERR))
#     car.online = int(online)
#     db.session.add(car)
#     db.session.commit()
#     write_redis_message_order("1", {"type": "1", "online": int(online), "deviceid": carId})
#     return jsonify(code=RET.OK, msg=error_map.get(RET.OK))
# except Exception as e:
#     print(e)
#     db.session.rollback()
#     return jsonify(code=RET.DBERR, msg=error_map.get(RET.DBERR))
# if update_online_decice(type=type, online=int(online), deviceid=carId):
#     return jsonify(code=RET.OK, msg=error_map.get(RET.OK))
# else:
#     return jsonify(code=RET.DBERR, msg=error_map.get(RET.DBERR))


# @car_info.route('/demo/', methods=["get"])
# def demo():
#     return render_template("socketiodemo.html")
