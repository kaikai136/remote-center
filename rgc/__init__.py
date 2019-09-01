# -*- coding：utf8 -*-
# @Time : 2019/5/8 18:52 
# @Author : muyongzhen
# @File : __init__.py.py
import sys

from flask import Flask, make_response
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
from redis import StrictRedis
from settings import config_dict
import os

'''导入顺序'''
db = SQLAlchemy()
from rgc.model.models import *


def redis_init(config_name):
    redis_store = StrictRedis(host=config_dict[config_name].REDIS_HOST, port=config_dict[config_name].REDIS_PORT,
                              db=config_dict[config_name].REDIS_DB, decode_responses=True)
    return redis_store


# redis_store = redis_init('development')
redis_store = redis_init('production')


def setup_log(config_name):
    """配置日志"""
    if not os.path.exists("./logs"):
        os.mkdir("./logs")
    logging.basicConfig(level=config_dict[config_name].LOG_LEVEL, datefmt='%Y-%m-%d %H:%M:%S')
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10, encoding='UTF-8')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s')
    file_log_handler.setFormatter(formatter)
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    # setup_log(config_name)

    if getattr(sys, 'frozen', False):
        template_folder = os.path.join(sys._MEIPASS, 'templates')
        static_folder = os.path.join(sys._MEIPASS, 'static')
        app = Flask(__name__, template_folder=template_folder, static_folder=static_folder, static_url_path='')
    else:
        app = Flask(__name__, static_url_path='')

    app.config.from_object(config_dict[config_name])
    Session(app)
    # 跨域
    CORS(app, supports_credentials=True)

    db.init_app(app)

    from rgc.views.user import user_info
    app.register_blueprint(user_info, url_prefix="/api")

    from rgc.views.car import car_info
    app.register_blueprint(car_info, url_prefix="/api")

    from rgc.views.connectdevice import conn_info
    app.register_blueprint(conn_info, url_prefix="/api")

    from rgc.views.platform.views import platform_info
    app.register_blueprint(platform_info, url_prefix="/api")

    from rgc.views.validation import validation_blue
    app.register_blueprint(validation_blue, url_prefix="/api")

    return app

