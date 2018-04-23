Go to http://graphql.cn/learn/ to learn.

Token认证：
.........................
首先访问 /login 地址，登入成功后放回带token的json数据（ps:token有效期为1小时）

访问/graphql时候，在请求头加上Authorization：'JWT ' + token

后台验证token成功后正常访问/graphql地址，验证错误返回错误信息：
{'status': False, 'data': '', 'msg': '请传递正确的验证头信息'}


API接口：
.........................
- 登入地址::

    /login
    method:POST
    response:
        {
            "data": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1MjQ0NTExMjIsImlhdCI6MTUyNDQ0NzUyMiwiaXNzIjoiYWRtaW4iLCJkYXRhIjp7ImlkIjoiMSIsImxvZ2luX3RpbWUiOjE1MjQ0NDc1MjJ9fQ.6uHINYj4h5EYKNL03pNe3MAqfYFqdnQgXApHgythW1s",
            "msg": "登录成功",
            "status": true
        }

- 查询拼接::

    {
      admins(id: "1") {
        edges {
          node {
            email
            name
          }
        }
      }
      books(name:"百年孤独") {
        edges {
          node {
            id, name, title, price
          }
        }
      }
    }

- 分页查询, 排序(first:从第5个数据开始查询， last:第5个数据往前5个数据， order：根据create_time字段降序查询，去掉‘-’为升序)::

    {books (first: 5, last:5, order:"-create_time") {
      totalCount
       edges {
         node {
           id, name, title, price
        }
      }
    }}

- 添加图书::

   mutation {
     addBook(name:"活着",author:"余华",price:23,
                        title:"") {
       book {
         id
         author
         price
       }
     }
   }