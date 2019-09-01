# -*- coding：utf8 -*-
# @Project : remote-center
# @Author : qxq
# @Time : 2019/7/2 9:42 AM


from flask import Blueprint

validation_blue = Blueprint("validation_blue", __name__)

from . import views