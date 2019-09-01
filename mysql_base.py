#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re

import pymysql, os, configparser
from pymysql.cursors import DictCursor
from DBUtils.PooledDB import PooledDB

DBHOST = os.getenv('DBHOST', '192.168.245.8')
DBPORT = os.getenv('DBPORT', '3306')
DBUSER = os.getenv('DBUSER', "root")
DBPWD = os.getenv('DBPWD', "mysql")
DBNAME = os.getenv('DBNAME', "registrycenter")
DBCHAR = os.getenv('DBCHAR', "utf8")


class BasePymysqlPool(object):
    def __init__(self, host, port, user, password, db_name=None):
        self.db_host = host
        self.db_port = int(port)
        self.user = user
        self.password = str(password)
        self.db = db_name
        self.conn = None
        self.cursor = None


class MyPymysqlPool(BasePymysqlPool):
    """
    MYSQL数据库对象，负责产生数据库连接 , 此类中的连接采用连接池实现获取连接对象：conn = Mysql.getConn()
            释放连接对象;conn.close()或del conn
    """
    # 连接池对象
    __pool = None

    def __init__(self, conf_name=None):
        # self.conf = Config().get_content(conf_name)
        self.conf = {
            'host': DBHOST,
            'port': DBPORT,
            'user': DBUSER,
            'password': DBPWD,
            'db_name': DBNAME
        }

        super(MyPymysqlPool, self).__init__(**self.conf)
        # 数据库构造函数，从连接池中取出连接，并生成操作游标
        self._conn = self.__getConn()
        self._cursor = self._conn.cursor()

    def __getConn(self):
        """
        @summary: 静态方法，从连接池中取出连接
        @return MySQLdb.connection
        """
        if MyPymysqlPool.__pool is None:
            MyPymysqlPool.__pool = PooledDB(creator=pymysql,
                                            maxconnections=6,  # 连接池允许的最大连接数，0和None表示不限制连接数
                                            mincached=1,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
                                            maxcached=20,  # 链接池中最多闲置的链接，0和None不限制
                                            maxshared=3,
                                            # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的 threadsafety都为1，所有值无论设置为多少，_maxcached永远为0，所以永远是所有链接都共享。
                                            blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
                                            maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制

                                            host=self.db_host,
                                            port=self.db_port,
                                            user=self.user,
                                            passwd=self.password,
                                            db=self.db,
                                            use_unicode=True,
                                            charset="utf8",
                                            cursorclass=DictCursor)
        return MyPymysqlPool.__pool.connection()

    def getAll(self, sql, param=None):
        """
        @summary: 执行查询，并取出所有结果集
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list(字典对象)/boolean 查询到的结果集
        """
        self.start()
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchall()
        else:
            result = False
        self.dispose()
        return result, count

    def getOne(self, sql, param=None):
        """
        @summary: 执行查询，并取出第一条
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        self.start()
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchone()
        else:
            result = False
        self.dispose()
        return result

    def getMany(self, sql, num, param=None):
        """
        @summary: 执行查询，并取出num条结果
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param num:取得的结果条数
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        self.start()
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchmany(num)
        else:
            result = False
        self.dispose()
        return result

    def insertMany(self, sql, values):
        """
        @summary: 向数据表插入多条记录
        @param sql:要插入的ＳＱＬ格式
        @param values:要插入的记录数据tuple(tuple)/list[list]
        @return: count 受影响的行数
        """
        self.start()
        count = self._cursor.executemany(sql, values)
        self.dispose()
        return count

    def __query(self, sql, param=None):
        self.start()
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        self.dispose()
        return count

    def update(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def insert(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def delete(self, sql, param=None):
        """
        @summary: 删除数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要删除的条件 值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def execute(self, sql, param=None):
        return self.__query(sql, param)

    def begin(self):
        """
        @summary: 开启事务
        """
        self._conn.autocommit(0)

    def end(self, option='commit'):
        """
        @summary: 结束事务
        """
        if option == 'commit':
            self._conn.commit()
        else:
            self._conn.rollback()

    def start(self):
        self._conn = self.__getConn()
        self._cursor = self._conn.cursor()

    def dispose(self, isEnd=1):
        """
        @summary: 释放连接池资源
        """
        if isEnd == 1:
            self.end('commit')
        else:
            self.end('rollback')
        self._cursor.close()
        self._conn.close()


def getDB():
    return MyPymysqlPool()


def sqlr(sql, data):
    m = re.findall(r'(\$\w+)', sql)
    for i in m:
        val = "\"%s\"" % eval("data.%s" % i.replace('$', ''))
        sql = sql.replace(i, val)

    m = re.findall(r'(\#\w+)', sql)
    for i in m:
        val = eval("data.%s" % i.replace('#', ''))
        sql = sql.replace(i, val)

    return sql


def sqlk(sql, **pars):
    m = re.findall(r'(\$\w+)', sql)
    for i in m:
        key = i.replace('$', '')
        val = "\"%s\"" % pars[key]
        sql = sql.replace(i, val)

    m = re.findall(r'(\#\w+)', sql)
    for i in m:
        key = i.replace('#', '')
        val = pars[key]
        sql = sql.replace(i, val)

    return sql


if __name__ == '__main__':
    mysql = getDB()
    '''
    数据库进行修改
    '''
    sql = 'select app_key from appinfo;'
    result, count = mysql.getAll(sql)
    print(444, result)
