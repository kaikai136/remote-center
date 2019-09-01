# -*- coding：utf8 -*-
# @Time : 2019/5/10 14:43 
# @Author : muyongzhen
# @File : __init__.py.py 
from flask import Blueprint

conn_info = Blueprint("conn_info", __name__)

from . import views