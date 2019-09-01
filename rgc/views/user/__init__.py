# -*- coding：utf8 -*-
# @Time : 2019/5/10 10:19 
# @Author : muyongzhen
# @File : __init__.py.py

from flask import Blueprint

user_info = Blueprint("user_info", __name__)

from . import views