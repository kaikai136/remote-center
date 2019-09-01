# -*- coding：utf8 -*-
# @Time : 2019/5/13 13:51 
# @Author : muyongzhen
# @File : __init__.py.py 
from flask import Blueprint

platform_info = Blueprint("platform_info", __name__)

from . import views