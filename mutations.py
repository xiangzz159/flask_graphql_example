# ！/usr/bin/env python
# _*_ coding:utf-8 _*_

'''

@author: yerik

@contact: xiangzz159@qq.com

@time: 2018/4/20 14:07

@desc: 业务逻辑代码

'''

import graphene
import models
import hashlib
import time
import uuid
import api
from config import db_session
from auths import Auth


def new_id():
    return uuid.uuid4().hex


def encryption_md5(str):
    if str is None:
        return None
    hl = hashlib.md5()
    hl.update(str.encode(encoding='utf-8'))
    return hl.hexdigest()


# 业务逻辑代码：增删改等错做
class addBook(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        author = graphene.String()
        title = graphene.String()
        price = graphene.Int()

    ok = graphene.Boolean()
    book = graphene.Field('api.Book')

    def mutate(self, info, name, author, price, title=None):
        create_time = update_time = time.time()
        id = new_id()
        book = models.ExchangeAccount(id=id, name=name, title=title,
                                      price=price, author=author, del_flag=1, create_time=create_time,
                                      update_time=update_time)
        db_session.add(book)
        db_session.commit()
        return addBook(book=book)


class MyMutations(graphene.ObjectType):
    add_book = addBook.Field()
