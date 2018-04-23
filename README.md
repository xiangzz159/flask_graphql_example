#flask_graphql_example

While you are at it you could ensure that you are using the latest `pip` version

    pip install --upgrade pip

Then install required python libraries

    pip install -r requirements.txt


中文：
本系统结合flask + SQLAlchemy + graphql + jwt(token验证）,对/graphql接口进行用户验证

通过/login 接口登入，成功返回带token的json数据。

然后将得到的token放在http请求头里面，格式：Authorization：'JWT ' + token

系统将会验证token，成功则能正常访问/graphql， 验证失败则返回带错误信息的json数据

en:
This project is integrated flask + SQLAlchemy + graphql + jwt(Login authentication)， Perform user validation on /graphql interfaces.

Login admin and return json with token,

and then request /graphql with request head {Authorization：'JWT ' + token}

project will validation token,  if successful, visit baidu.else, return error message


