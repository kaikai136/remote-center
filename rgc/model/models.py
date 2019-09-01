# -*- coding：utf8 -*-
# @Time : 2019/5/8 18:54 
# @Author : muyongzhen
# @File : models.py 

from rgc import db
import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from settings import Config
from sqlalchemy import or_, and_

class UserInfo(db.Model):
    __tablename__ = "userinfo"
    id = db.Column(db.Integer, primary_key=True)
    # 用户名
    username = db.Column(db.String(32), unique=True, index=True, nullable=False)
    # 密码
    pwd = db.Column(db.String(32), index=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "pwd": self.pwd
        }

    def generate_user_token(self, expiration=Config.EXPIRATION):
        s = Serializer(Config.SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': self.id, 'username': self.username}).decode('utf-8')

    @staticmethod
    def verify_user_token(token):
        s = Serializer(Config.SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = UserInfo.query.get(data['id'])
        return user


class CarInfo(db.Model):
    __tablename__ = 'carinfo'
    id = db.Column(db.Integer, primary_key=True)
    # 车辆id
    carId = db.Column(db.String(32), unique=True, index=True, nullable=False)
    # 车辆ip
    carIp = db.Column(db.String(32), index=True, nullable=False)
    # 车辆牌照
    carLicense = db.Column(db.String(32), index=True, nullable=False)
    # 在线状态
    online = db.Column(db.Boolean(), default=False, nullable=False)
    # 创建时间
    create_at = db.Column(db.DateTime, default=datetime.datetime.now())

    def to_dict(self):
        return {
            "id": self.id,
            "carId": self.carId,
            "carIp": self.carIp,
            "carLicense": self.carLicense,
            "online": 1 if self.online else 0,
            "create_at": self.create_at.strftime("%Y-%m-%d %H:%M:%S")
        }

    def get_app_key(self):
        app = AppInfo.query.filter(and_(AppInfo.type == "1", AppInfo.deviceId == self.carId)).first()
        if app:
            return app.app_key
        else:
            return ""

    def get_app_secret(self):
        app = AppInfo.query.filter(and_(AppInfo.type == "1", AppInfo.deviceId == self.carId)).first()
        if app:
            return app.app_secret
        else:
            return ""


class PlatformInfo(db.Model):
    __tablename__ = 'platforminfo'
    id = db.Column(db.Integer, primary_key=True)
    # 架台id
    platformId = db.Column(db.String(32), unique=True, index=True, nullable=False)
    # 架台名称
    platformName = db.Column(db.String(32), index=True, nullable=False)
    # 架台ip
    platformIp = db.Column(db.String(32), index=True, nullable=False)
    # 解析端口
    parsePort = db.Column(db.String(32), index=True, nullable=False)
    # 在线状态
    online = db.Column(db.Boolean(), default=False)
    # 创建时间
    create_at = db.Column(db.DateTime, default=datetime.datetime.now())

    def to_dict(self):
        return {
            "id": self.id,
            "platformId": self.platformId,
            "platformName": self.platformName,
            "platformIp": self.platformIp,
            "parsePort": self.parsePort,
            "online": 1 if self.online else 0,
            "create_at": self.create_at.strftime("%Y-%m-%d %H:%M:%S")
        }

    def get_app_key(self):
        app = AppInfo.query.filter(and_(AppInfo.type == "2", AppInfo.deviceId == self.platformId)).first()
        if app:
            return app.app_key
        else:
            return ""

    def get_app_secret(self):
        app = AppInfo.query.filter(and_(AppInfo.type == "2", AppInfo.deviceId == self.platformId)).first()
        if app:
            return app.app_secret
        else:
            return ""



class ConnectDevice(db.Model):
    __tablename__ = 'connectdevice'
    id = db.Column(db.Integer, primary_key=True)
    # 车辆的id carID
    car_id = db.Column(db.String(32), index=True, nullable=False)
    # 台架的id  platformId
    platform_id = db.Column(db.String(32), index=True, nullable=False)
    # 连接时间
    create_at = db.Column(db.DateTime, default=datetime.datetime.now())


class AppInfo(db.Model):
    __tablename__ = "appinfo"
    id = db.Column(db.Integer, primary_key=True)
    app_key = db.Column(db.String(32), unique=True, index=True, nullable=True)
    app_secret = db.Column(db.String(128), index=True, nullable=True)
    # 1车，2架台
    type = db.Column(db.String(1), index=True, nullable=True)
    # carId, platformId
    deviceId = db.Column(db.String(32), index=True, nullable=True)

"""base64.b64encode(bytes(hashlib.md5(bytes("appid", encoding="utf8")).hexdigest(), encoding="utf8"))"""
