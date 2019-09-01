# -*- coding：utf8 -*-
# @Time : 2019/5/10 10:19 
# @Author : muyongzhen
# @File : views.py 
from flask import jsonify, current_app, request, session, g
from rgc import db
from rgc.model.models import UserInfo
from rgc.tools.response_code import RET, error_map
from rgc.views.user import user_info


@user_info.route("/login/", methods=["POST"])
def user_login_request():
    username = request.form.get("username")
    pwd = request.form.get("pwd")
    if not all([username, pwd]):
        return jsonify(code=RET.PARAMERR, msg=error_map.get(RET.PARAMERR))

    try:
        user = UserInfo.query.filter(UserInfo.username==username).first()
        if not user:
            return jsonify(code=RET.PARAMERR, msg="用户名不存在")
        if user.pwd != pwd:
            return jsonify(code=RET.PARAMERR, msg="密码不正确")
        session["userinfo"] = user.to_dict()
        session["userid"] = user.id
        g.user = user
        token = user.generate_user_token()
    except Exception as e:
        # print(e)
        current_app.logger.error(e)
        return jsonify(code=RET.DBERR, msg=error_map.get(RET.DBERR))
    return jsonify(code=RET.OK, msg=error_map.get(RET.OK), token=token)


@user_info.route("/logout/", methods=["get"])
def user_logout_request():
    session.clear()
    return jsonify(code=RET.OK, msg=error_map.get(RET.OK))