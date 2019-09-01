# -*- coding：utf8 -*-
# @Project : remote-center
# @Author : qxq
# @Time : 2019/7/2 9:50 AM
from flask import request, current_app
from rgc import PlatformInfo, AppInfo, CarInfo
from rgc.views.validation import validation_blue


@validation_blue.route("/platisonline/", methods=["POST"])
def plat_is_online():
    ip = request.form.get('ip')
    if not ip:
        return '1'
    try:
        platform_obj = PlatformInfo.query.filter(PlatformInfo.platformIp == ip).all()
    except Exception as e:
        current_app.logger.error(e)
        return '2'

    if not platform_obj:
        pass
    else:
        for platform in platform_obj:
            if platform.online:
                return '3'
    return '4'


@validation_blue.route("/carisonline/", methods=["POST"])
def car_is_online():
    ip = request.form.get('ip')
    print(ip)
    if not ip:
        return '1'
    try:
        car_obj = CarInfo.query.filter(CarInfo.carIp == ip).all()
    except Exception as e:
        current_app.logger.error(e)
        return '2'

    if not car_obj:
        pass
    else:
        for car in car_obj:
            if car.online:
                return '3'
    return '4'


@validation_blue.route("/isonline/", methods=["POST"])
def is_online():
    app_key = request.form.get('app_key')
    if not app_key:
        return '4'
    try:
        app_obj = AppInfo.query.filter(AppInfo.app_key == app_key).first()
    except Exception as e:
        current_app.logger.error(e)
        return '2'
    if not app_obj:
        pass
    else:
        type = app_obj.type
        id = app_obj.deviceId
        if type == '1':
            try:
                car_obj = CarInfo.query.filter(CarInfo.carId == id).first()
            except Exception as e:
                current_app.logger.error(e)
                return '2'
            if not car_obj:
                pass
            else:
                if car_obj.online:
                    return '3'
        elif type == '2':
            try:
                plat_obj = PlatformInfo.query.filter(PlatformInfo.platformId == id).first()
            except Exception as e:
                current_app.logger.error(e)
                return '2'
            if not plat_obj:
                pass
            else:
                if plat_obj.online:
                    return '3'
        else:
            return '2'
    return '4'


@validation_blue.route("/platValidationKeySerect/", methods=["POST"])
def plat_validation_key_serect():
    app_key = request.form.get('app_key')
    app_secret = request.form.get('app_secret')
    if not all([app_key, app_secret]):
        return '1'
    try:
        app_obj = AppInfo.query.filter(AppInfo.app_key == app_key).first()
    except Exception as e:
        current_app.logger.error(e)
        return '2'
    if not app_obj:
        return '2'
    if app_obj.type != '2':
        return '2'
    if app_obj.app_secret != app_secret:
        return '3'

    try:
        deviceId = app_obj.deviceId
        platform_obj = PlatformInfo.query.filter(PlatformInfo.platformId == deviceId).first()
    except Exception as e:
        current_app.logger.error(e)
        return '2'

    if not platform_obj:
        return '2'
    return '4'


@validation_blue.route("/carValidationKeySerect/", methods=["POST"])
def car_validation_key_serect():
    app_key = request.form.get('app_key')
    app_secret = request.form.get('app_secret')
    if not all([app_key, app_secret]):
        return '1'

    try:
        app_obj = AppInfo.query.filter(AppInfo.app_key == app_key).first()
    except Exception as e:
        current_app.logger.error(e)
        return '2'
    if not app_obj:
        return '2'
    if app_obj.type != '1':
        return '2'
    if app_obj.app_secret != app_secret:
        return '3'

    try:
        deviceId = app_obj.deviceId
        car_obj = CarInfo.query.filter(CarInfo.carId==deviceId).first()
    except Exception as e:
        current_app.logger.error(e)
        return '2'
    if not car_obj:
        return '2'
    return '4'





