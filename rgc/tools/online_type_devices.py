# -*- coding：utf8 -*-
# @Time : 2019/5/24 10:29 
# @Author : muyongzhen
# @File : online_type_devices.py 
from rgc import db
from rgc.model.models import ConnectDevice, CarInfo, PlatformInfo
from rgc.tools.redis_message_order import write_redis_message_order

"""小车或架台异常掉线  需要传入当前设备的下线状态，和掉线前对应连接设备的上线状态（如何当前设备是连接状态时意外下线）"""


def update_online_decice(type, online, deviceid, name=""):
    """更新设备的状态
    type: 1车辆，2架台
    online:
    deviceid: 设备id
    """
    if type == "1":
        """车辆"""
        if online == 1:
            try:
                car = CarInfo.query.filter(CarInfo.carId == deviceid).first()
                if car:
                    car.online = 1
                    db.session.add(car)
                    db.session.commit()
                    write_redis_message_order(type="1", msg={"type": "1", "online": 1, "deviceid": deviceid})
                return True
            except Exception as e:
                db.session.rollback()
                print(e)
                return False
        elif online == 0:
            try:
                car = CarInfo.query.filter(CarInfo.carId == deviceid).first()
                if car:
                    car.online = 0
                    db.session.add(car)
                    db.session.commit()
                conn = ConnectDevice.query.filter(ConnectDevice.car_id == deviceid).first()
                if conn:
                    db.session.delete(conn)
                    db.session.commit()
                    write_redis_message_order(type="1", msg={"type": "2", "online": 1, "deviceid": conn.platform_id})
                write_redis_message_order(type="1", msg={"type": "1", "online": 0, "deviceid": deviceid})
                return True
            except Exception as e:
                print(e)
                db.session.rollback()
                return False
    elif type == "2":
        """台架"""
        if online == 1:
            try:
                plat = PlatformInfo.query.filter(PlatformInfo.platformId == deviceid).first()
                if plat:
                    plat.online = 1
                    if name:
                        plat.platformName = name
                    db.session.add(plat)
                    db.session.commit()
                    write_redis_message_order(type="1", msg={"type": "2", "online": 1, "deviceid": deviceid})
                    return True
            except Exception as e:
                db.session.rollback()
                print(e)
                return False
        elif online == 0:
            try:
                plat = PlatformInfo.query.filter(PlatformInfo.platformId == deviceid).first()
                if plat:
                    plat.online = 0
                    if name:
                        plat.platformName = name
                    db.session.add(plat)
                    db.session.commit()
                conn = ConnectDevice.query.filter(ConnectDevice.platform_id == deviceid).first()
                if conn:
                    db.session.delete(conn)
                    db.session.commit()
                    write_redis_message_order(type="1", msg={"type": "1", "online": 1, "deviceid": conn.car_id})
                write_redis_message_order(type="1", msg={"type": "2", "online": 0, "deviceid": deviceid})
                return True
            except Exception as e:
                print(e)
                db.session.rollback()
                return False
