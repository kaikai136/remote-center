# -*- coding：utf8 -*-
# @Time : 2019/5/13 13:51 
# @Author : muyongzhen
# @File : views.py 
import datetime
import json
import random
import time
import uuid
from flask import request, current_app, jsonify
from sqlalchemy import and_, or_
import re
from rgc import db
from rgc.model.models import PlatformInfo, ConnectDevice, AppInfo
from rgc.tools.response_code import RET, error_map
from rgc.tools.utils import is_login, get_16_md5
from rgc.tools.redis_message_order import write_redis_message_order
from rgc.views.platform import platform_info


@platform_info.route("/getPlatformlist/", methods=["get"])
@is_login
def get_platform_list_request():
    """获取台架列表
    type: 2:只显示在线的，3：只显示不在线的，其他全显示
    """
    type = request.args.get("type", "1")
    try:
        conns = ConnectDevice.query.all()
        conn_platform_id_list = [conn.platform_id for conn in conns]
        if type == "2":
            platforms = PlatformInfo.query.filter(PlatformInfo.online == 1).all()
        elif type == "3":
            platforms = PlatformInfo.query.filter(PlatformInfo.online == 0).all()
        else:
            platforms = PlatformInfo.query.all()
        platform_list = list()
        for platform in platforms:
            item = platform.to_dict()
            if platform.platformId in conn_platform_id_list:
                item["is_conn"] = 1
            else:
                item["is_conn"] = 0
            item["app_key"] = platform.get_app_key()
            item["app_secret"] = platform.get_app_secret()
            platform_list.append(item)
        return jsonify(code=RET.OK, msg=error_map.get(RET.OK), data=platform_list[::-1])
    except Exception as e:
        # print(e)
        current_app.logger.error(e)
        return jsonify(code=RET.DBERR, msg=error_map.get(RET.DBERR))


@platform_info.route("/getPlatforminfo/", methods=["get"])
@is_login
def get_platforminfo_request():
    """获取架台信息"""
    platformId = request.args.get("platformId", None)
    if not platformId:
        return jsonify(code=RET.PARAMERR, msg=error_map.get(RET.PARAMERR))
    try:
        conns = ConnectDevice.query.all()
        conn_platform_id_list = [conn.platform_id for conn in conns]
        platform = PlatformInfo.query.filter(PlatformInfo.platformId==platformId).first()
        if not platform:
            return jsonify(code=RET.PARAMERR, msg=error_map.get(RET.PARAMERR))
        data = platform.to_dict()
        if platformId in conn_platform_id_list:
            data["is_conn"] = 1
        else:
            data["is_conn"] = 0
        data["app_key"] = platform.get_app_key()
        data["app_secret"] = platform.get_app_secret()
    except Exception as e:
        # print(e)
        current_app.logger.error(e)
        return jsonify(code=RET.DBERR, msg=error_map.get(RET.DBERR))
    return jsonify(code=RET.OK, msg=error_map.get(RET.OK), data=data)


@platform_info.route("/PlatformAdd/", methods=["post"])
@is_login
def platform_add_request():
    """新增架台"""
    # platformId = request.form.get("platformId")
    platformName = request.form.get("platformName")
    # platformIp = request.form.get("platformIp")
    # parsePort = request.form.get("parsePort")

    plat_last = PlatformInfo.query.filter().order_by(PlatformInfo.platformId.desc()).first()
    if not plat_last:
        platformId = '0001'
    else:
        platformId = '%04d' % (int(plat_last.platformId) + 1)

    if not platformId:
        return jsonify(code=RET.PARAMERR, msg="台架ID不可为空")
    if not platformName:
        return jsonify(code=RET.PARAMERR, msg="台架名称不可为空")
    res_platformId = re.match("^[0-9]{3,6}$", platformId)
    if not res_platformId:
        return jsonify(code=RET.PARAMERR, msg='台架ID格式错误（只可包含数字）')

    re_platformName = re.match(r"^[\u4E00-\u9FA5a-zA-Z0-9]{1}[\u4E00-\u9FA5a-zA-Z0-9_]{2,7}$", platformName)
    if not re_platformName:
        return jsonify(code=RET.PARAMERR, msg='台架名称格式错误')

    parsePort = "6089"
    print('ssss', platformId, type(platformId))
    try:
        platformall = PlatformInfo.query.all()
        allips = [p.platformIp for p in platformall]
        while True:
            platformIp = "192.168.50.{}".format(random.randint(0, 256))
            if platformIp not in allips:
                break

        plat1 = PlatformInfo.query.filter(PlatformInfo.platformId==platformId).first()
        if plat1:
            return jsonify(code=RET.PARAMERR, msg="台架ID已存在，请更换有效ID。")
        plat2 = PlatformInfo.query.filter(PlatformInfo.platformName==platformName).first()
        if plat2:
            return jsonify(code=RET.PARAMERR, msg="台架名称已存在，请更换有效名称。")
        plat = PlatformInfo()
        plat.platformId = platformId
        plat.platformName = platformName
        plat.platformIp = platformIp
        plat.parsePort = parsePort
        plat.online = 0
        plat.create_at = datetime.datetime.now()
        app = AppInfo()
        app.type = "2"
        print(platformId, type(platformId))
        app.deviceId = platformId
        # app.app_key = get_16_md5(f"{int(time.time()*100)}{platformId}")
        # app.app_secret = str(uuid.uuid4().hex)

        app_key = get_16_md5("{}{}".format(int(time.time()*100), platformId))
        app.app_key = app_key
        # app.app_secret = get_16_md5(f"{app_key}{platformId}")
        app.app_secret = get_16_md5("{}{}".format(app_key, platformId))
        db.session.add(plat)
        db.session.add(app)
        db.session.commit()
        msg = {"type": "2", "online": 0, "deviceid": platformId}
        write_redis_message_order(type="1", msg=msg)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(code=RET.DBERR, msg=error_map.get(RET.DBERR))
    return jsonify(code=RET.OK, msg="台架添加成功")


@platform_info.route("/updatePlatformInfo/", methods=["post"])
@is_login
def platform_update_request():
    """修改架台信息"""
    # platformId = request.form.get("platformId")
    platformName = request.form.get("platformName")
    id = request.form.get("id")
    if not id:
        return jsonify(code=RET.PARAMERR, msg="id不能为空")
    # if not platformId:
    #     return jsonify(code=RET.PARAMERR, msg="台架ID不可为空")
    if not platformName:
        return jsonify(code=RET.PARAMERR, msg="台架名称不可为空")

    # res_platformId = re.match("^[0-9]{3,6}$", platformId)
    # if not res_platformId:
    #     return jsonify(code=RET.PARAMERR, msg='台架ID格式错误（3-6位纯数字）')

    re_platformName = re.match(r"^[\u4E00-\u9FA5a-zA-Z0-9]{1}[\u4E00-\u9FA5a-zA-Z0-9_]{2,7}$", platformName)
    if not re_platformName:
        return jsonify(code=RET.PARAMERR, msg='台架名称格式错误')

    try:
        plat1 = PlatformInfo.query.filter(PlatformInfo.id==id).first()
        if not plat1:
            return jsonify(code=RET.PARAMERR, msg='该台架不存在')

        if plat1.online:
            return jsonify(code=RET.PARAMERR, msg='台架在线不能操作')

        # plat3 = PlatformInfo.query.filter(and_(PlatformInfo.id != id,
        #                                        PlatformInfo.platformId == platformId)).first()
        # if plat3:
        #     return jsonify(code=RET.PARAMERR, msg="台架ID已存在，请更换有效ID")

        plat2 = PlatformInfo.query.filter(and_(PlatformInfo.id!=id,
                                               PlatformInfo.platformName==platformName)).first()
        if plat2:
            return jsonify(code=RET.PARAMERR, msg="台架名称已存在，请更换有效名称")

        old_platformid = plat1.platformId
        # app = AppInfo.query.filter(and_(AppInfo.type=="2", AppInfo.deviceId==old_platformid)).first()
        # app.deviceId = platformId
        # db.session.add(app)
        # plat1.platformId = platformId
        plat1.platformName = platformName
        db.session.add(plat1)
        db.session.commit()
        write_redis_message_order(type="1", msg={"type": "2", "online": 0, "deviceid": old_platformid})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(code=RET.DBERR, msg=error_map.get(RET.DBERR))
    return jsonify(code=RET.OK, msg="修改保存成功")


@platform_info.route("/PlatformDelete/", methods=["get"])
@is_login
def platform_delete_request():
    """删除架台"""
    platformId = request.args.get("platformId")
    if not platformId:
        return jsonify(code=RET.PARAMERR, msg=error_map.get(RET.PARAMERR))
    try:
        conn = ConnectDevice.query.filter(ConnectDevice.platform_id==platformId).first()
        if conn:
            return jsonify(code=RET.PARAMERR, msg="台架已连接，请先断开")
        plat = PlatformInfo.query.filter(PlatformInfo.platformId==platformId).first()
        if not plat:
            return jsonify(code=RET.PARAMERR, msg=error_map.get(RET.PARAMERR))
        app = AppInfo.query.filter(and_(AppInfo.deviceId==platformId, AppInfo.type=="2")).first()
        if app:
            db.session.delete(app)
        db.session.delete(plat)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(code=RET.DBERR, msg=error_map.get(RET.DBERR))
    return jsonify(code=RET.OK, msg=error_map.get(RET.OK))
