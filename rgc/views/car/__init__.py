# -*- coding：utf8 -*-
# @Time : 2019/5/8 18:55 
# @Author : muyongzhen
# @File : __init__.py.py 
from flask import Blueprint

car_info = Blueprint("car_info", __name__)

from . import views