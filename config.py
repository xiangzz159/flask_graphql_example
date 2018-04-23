# ！/usr/bin/env python
# _*_ coding:utf-8 _*_

'''

@author: yerik

@contact: xiangzz159@qq.com

@time: 2018/4/22 13:48

@desc: 配置

'''

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
import config

# 数据库
DB_USER = 'root'
DB_PASSWORD = ''
DB_HOST = 'localhost'
DB_PORT = 3306
DB_NAME = 'Your_DB_Name'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + DB_USER + ':' + DB_PASSWORD + '@' + DB_HOST + ':' + str(
    DB_PORT) + '/' + DB_NAME + '?charset=utf8'

# Redis
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_PASSWORD = ''

# APP启动
APP_HOST = '0.0.0.0'
APP_PORT = 8000

# 生成认证token-secret_key
SECRET_KEY = "SECRET_KEY"

# 开启访问拦截
BEFOR_REQUEST = True
# 开启过期时间验证
VERIFY_EXP = True

# 数据库连接
engine = create_engine(config.SQLALCHEMY_DATABASE_URI, convert_unicode=True)
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base(bind=engine)
Base.query = db_session.query_property()

# redis连接
# pool = redis.ConnectionPool(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)
# r = redis.Redis(connection_pool=pool)


def trueReturn(data, msg):
    return {
        "status": True,
        "data": data,
        "msg": msg
    }


def falseReturn(data, msg):
    return {
        "status": False,
        "data": data,
        "msg": msg
    }


