#! /usr/bin/python
# -*- coding:utf-8 -*-
import time
from threading import Lock
from flask import current_app, render_template
# from flask_socketio import SocketIO
# from RegistrationService import main
from rgc import create_app, db
from rgc.model.models import CarInfo, PlatformInfo, ConnectDevice
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from rgc.tools.redis_message_order import read_redis_message_order, write_redis_message_order
from sqlalchemy import or_

# app = create_app('development')
app = create_app('production')

manager = Manager(app)

Migrate(app, db)
# 添加迁移命令
manager.add_command('db', MigrateCommand)

# socketio = SocketIO(logger=True, engineio_logger=True, ping_timeout=3600000, ping_interval=3600)
#socketio = SocketIO(ping_interval=3600)
#disconnected = None
#async_mode = None
#socketio.init_app(app, async_mode=async_mode)

thread = None
thread_lock = Lock()


# def back():
#     with app.app_context():
#         while True:
#             socketio.sleep(1)
#             msg = read_redis_message_order("1")
#             if not msg:
#                 # socketio.emit('server_response',{'data': ""}, broadcast=True)
#                 continue
#             print('msg', msg)
#             try:
#                 if msg["online"] == 0 and msg["type"] == "1":
#                     car = CarInfo.query.filter(CarInfo.carId == msg["deviceid"]).first()
#                     if car:
#                         car.online = 0
#                         db.session.add(car)
#                         db.session.commit()
#                 elif msg["online"] == 0 and msg["type"] == "2":
#                     print('台架下线')
#                     plat = PlatformInfo.query.filter(PlatformInfo.platformId == msg["deviceid"]).first()
#                     if plat:
#                         plat.online = 0
#                         db.session.add(plat)
#                         db.session.commit()
#                 elif msg["online"] == 1 and msg["type"] == "1":
#                     car = CarInfo.query.filter(CarInfo.carId == msg["deviceid"]).first()
#                     if car:
#                         car.online = 1
#                         db.session.add(car)
#                         db.session.commit()
#                 elif msg["online"] == 1 and msg["type"] == "2":
#                     print('台架上线')
#                     plat = PlatformInfo.query.filter(PlatformInfo.platformId == msg["deviceid"]).first()
#                     if plat:
#                         plat.online = 1
#                         db.session.add(plat)
#                         db.session.commit()
#                 if msg["online"] == 0:
#                     conn = ConnectDevice.query.filter(or_(ConnectDevice.car_id == msg["deviceid"],
#                                                           ConnectDevice.platform_id == msg["deviceid"])).first()
#                     if conn:
#                         if msg["type"] == "1":
#                             write_redis_message_order(type="1",
#                                                       msg={"type": "2", "deviceid": conn.platform_id, "online": 1})
#                         elif msg["type"] == "2":
#                             write_redis_message_order(type="1",
#                                                       msg={"type": "1", "deviceid": conn.car_id, "online": 1})
#                         db.session.delete(conn)
#                         db.session.commit()
#                 print('msg1', msg)
#                 socketio.emit('server_response', {'data': msg, "code": "200", 'msg': "OK"}, broadcast=True)
#                 # socketio.emit('server_response', {'data': msg, "code": "200", 'msg': "OK"}, namespace='/getdatalist')
#             except Exception as e:
#                 db.session.rollback()
#                 # print(e)
#                 current_app.logger.error(e)
#                 back()


# @socketio.on("connect")
# def get_data_list():
#     # print("ok")
#     global thread
#     with thread_lock:
#         if thread is None:
#             thread = socketio.start_background_task(target=back)


@app.route("/")
def index():
    return render_template('index.html')


if __name__ == '__main__':
    # from multiprocessing import Process
    # p_rs = Process(target=main)
    # p_rs.start()

    app.run(host="127.0.0.1", port=5000, debug=True)
    # manager.run()
    # p_rs1 = Process(target=socketio.run, args=(app, "0.0.0.0", 9903))
    # p_rs1.start()
    # socketio.run(app, host="0.0.0.0", port=9999)
    # python manage.py runserver -h 0.0.0.0 -p 9000
    # socketio.run(app)
    # pyinstaller -F manage.py --hidden-import=pymysql --add-data 'rgc/templates:templates' --add-data 'rgc/static:static' -n remotecenter

"""
迁移命令
python manage.py db init
python manage.py db migrate -m '描述'
python manage.py db upgrade
"""
