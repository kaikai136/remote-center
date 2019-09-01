# coding:utf-8


class RET:
    OK                  = 200
    DBERR               = 4001
    NODATA              = 4002
    DATAEXIST           = 4003
    DATAERR             = 4004
    PARAMERR            = 4005
    NETWORKERR          = 4006
    ACCESSERR           = 4007
    NOTLOGIN            = 4008


error_map = {
    RET.OK                    : u"成功",
    RET.DBERR                 : u"数据库查询/修改错误",
    RET.NODATA                : u"无数据",
    RET.DATAEXIST             : u"数据已存在",
    RET.DATAERR               : u"数据错误",
    RET.PARAMERR              : u"参数错误",
    RET.NETWORKERR            : u"网络异常",
    RET.ACCESSERR             : u"权限错误",
    RET.NOTLOGIN              : u"没有登录"
}
