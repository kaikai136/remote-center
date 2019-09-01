# -*- coding：utf8 -*-
# @Time : 2019/5/9 12:06 
# @Author : muyongzhen
# @File : utils.py

from flask import jsonify, session, g, request
from functools import wraps
from rgc.tools.response_code import RET, error_map
from rgc.model.models import UserInfo
import hashlib


def is_login(func):
    """检验登录状态"""

    @wraps(func)
    def check_login(*args, **kwargs):
        token = request.headers.get("token")
        if not token:
            return jsonify(code=RET.NOTLOGIN, msg=error_map.get(RET.NOTLOGIN))

        user = UserInfo.verify_user_token(token=token)

        if not user:
            return jsonify(code=RET.NOTLOGIN, msg=error_map.get(RET.NOTLOGIN))
        else:
            g.user = user
            return func(*args, **kwargs)

    return check_login


def get_16_md5(s):
    return hashlib.md5(bytes(s, encoding="utf8")).hexdigest()[:16]
