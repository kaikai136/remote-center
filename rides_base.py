from redis import Redis


# from Singleton import *
#
# @singleton
class REDIS(object):
    def __init__(self, host, port, password, db):
        self.__host = host
        self.__port = port
        self.__password = password
        self.__db = db

        try:
            self.__redis = Redis(host=host, port=self.__port, password=self.__password, db=self.__db)
        except Redis.Error as e:
            print("init error %d: %s" % (e.args[0], e.args[1]))

    def add(self, skey, sval):
        return self.__redis.sadd(skey, sval)

    # def sget(self, skey):
    #     return self.__redis.sget(skey)

    def count(self, skey):
        count = self.__redis.scard(skey)
        return count

    def members(self, skey):
        list = self.__redis.smembers(skey)
        return list

    def sdelete(self, skey):
        return self.__redis.spop(skey)

    def set(self, skey, sval, ex=None, px=None, nx=False, xx=False):
        return self.__redis.set(skey, sval, ex=None, px=None, nx=False, xx=False)

    def get(self, skey):
        return self.__redis.get(skey)

    def delete(self, skey):
        return self.__redis.delete(skey)

    def sremove(self, skey, object):
        return self.__redis.srem(skey, object)

    def expire(self, skey, ex):
        return self.__redis.expire(skey, ex)

    def rpush(self, key, value):
        self.__redis.rpush(key, value)

    def lpush(self, key, value):
        self.__redis.lpush(key, value)

    def read(self, key, start, stop):
        return self.__redis.lrange(key, start, stop)


# rds = REDIS("172.16.104.20", 6379,0)
rds = REDIS(host="192.168.245.4", port='6379', password='', db=1)

if __name__ == "__main__":
    rds.set('kaikai', 123, px=100)
    import time

    time.sleep(2)
    str = rds.get('kaikai')
    print(str)
    # rds.add("aa",1)
    # rds.add("aa",2)
    # rds.add("aa",3)
    # rds.add("aw",3)
    # print ("count:",rds.count("aa"))
    # print ("count:",rds.count("aw"))
    # print ("member:",rds.members("aa"))
    # print ("member:",rds.members("aw"))
    # print ("delete:",rds.delete("aa"))
    # print ("member:",rds.members("aa"))
