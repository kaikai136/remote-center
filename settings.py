#! /usr/bin/python
# -*- coding:utf-8 -*-
import redis
from redis import StrictRedis
import logging


class Config(object):
    SECRET_KEY = 'c0zUaBJUD4puChymzbr4fVXX1Wd/kxLmO3m48kD+oFG37nstiwJgU81qPDpPXykfBXNM62jPunzZD0NlZjdcl9ph'

    # 连接mysql数据库的配置
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:mysql@192.168.245.4:3306/registrycenter?charset=utf8"
    SQLALCHEMY_POOL_SIZE = 40
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_POOL_RECYCLE = 3600
    # 追踪对象得修改并且发送信号
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 定义redis的host, port, db
    REDIS_HOST = '192.168.245.4'
    REDIS_PORT = 6379
    REDIS_DB = 0
    # 有效时间session 一天
    PERMANENT_SESSION_LIFETIME = 24 * 60 * 60

    SESSION_TYPE = 'redis'
    # 配置session信息存储在哪个数据库
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)

    # token过期时间
    EXPIRATION = 60 * 60 * 24


class DevelopmentConfig(Config):
    """开发模式下的配置"""
    DEBUG = True
    # 日志等级默认为WARNING
    LOG_LEVEL = logging.DEBUG
    # LOG_LEVEL = logging.WARNING


class ProductionConfig(Config):
    """生产模式下的配置"""
    DEBUG = False
    LOG_LEVEL = logging.ERROR


# 定义字段，来映射不同的的配置类
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
