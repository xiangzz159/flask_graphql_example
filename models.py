#！/usr/bin/env python
# _*_ coding:utf-8 _*_

'''

@author: yerik

@contact: xiangzz159@qq.com

@time: 2018/4/19 15:13

@desc: Model层

'''

from sqlalchemy import Column, BigInteger, Integer, String
from config import Base, db_session

class Admin(Base):
    __tablename__ = 'admin'
    id = Column(String(64), primary_key=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    role_id = Column(Integer)
    role_name = Column(String(255))
    created_by = Column(String(64))
    last_modified_by = Column(String(64))
    del_flag = Column(Integer, default=1, nullable=False)
    create_time = Column(BigInteger)
    update_time = Column(BigInteger)

    def update(self):
        return db_session.commit()

    def get(self, id):
        admin = self.query.filter_by(id=id).first()
        return admin


class ExchangeAccount(Base):
    __tablename__ = 'book'
    id = Column(String(64), primary_key=True, nullable=False)
    name = Column(String(64), nullable=False)
    author = Column(String(64), nullable=False)
    title = Column(String(255))
    price = Column(Integer, nullable=False)
    del_flag = Column(Integer, default=1, nullable=False)
    create_time = Column(BigInteger)
    update_time = Column(BigInteger)


