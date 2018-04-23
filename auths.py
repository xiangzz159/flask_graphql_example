import jwt, datetime, time
from flask import jsonify
from models import Admin
import config
import base64
from Crypto.Cipher import AES


class Auth():
    @staticmethod
    def encode_auth_token(user_id, login_time):
        """
        生成认证Token
        :param user_id: int
        :param login_time: int(timestamp)
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, hours=1),  # 过期时间
                'iat': datetime.datetime.utcnow(),  # 表示当前时间在nbf里的时间之前，则Token不被接受
                'iss': 'admin',  # token签发者
                'data': {
                    'id': user_id,
                    'login_time': login_time
                }
            }
            return jwt.encode(
                payload,
                config.SECRET_KEY,
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        验证Token
        :param auth_token:
        :return: integer|string
        """
        try:
            # payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'), leeway=datetime.timedelta(seconds=10))
            payload = jwt.decode(auth_token, config.SECRET_KEY, options={'verify_exp': config.VERIFY_EXP})
            if ('data' in payload and 'id' in payload['data']):
                return payload
            else:
                raise jwt.InvalidTokenError
        except jwt.ExpiredSignatureError:
            return 'Token过期'
        except jwt.InvalidTokenError:
            return '无效Token'

    def identify(self, request):
        """
        用户鉴权
        :return: list
        """
        auth_header = request.headers.get('Authorization')
        if (auth_header):
            auth_tokenArr = auth_header.split(" ")
            if (not auth_tokenArr or auth_tokenArr[0] != 'JWT' or len(auth_tokenArr) != 2):
                result = config.falseReturn('', '请传递正确的验证头信息')
            else:
                auth_token = auth_tokenArr[1]
                payload = self.decode_auth_token(auth_token)
                if not isinstance(payload, str):

                    admin = Admin.get(Admin, payload['data']['id'])

                    if (admin is None):
                        result = config.falseReturn('', '找不到该用户信息')
                    else:
                        if (admin.update_time == payload['data']['login_time']):
                            result = config.trueReturn(admin.id, '请求成功')
                        else:
                            result = config.falseReturn('', 'Token已更改，请重新登录获取')
                else:
                    result = config.falseReturn('', payload)
        else:
            result = config.falseReturn('', '没有提供认证token')
        return result

    def authenticate(self, email, password):
        """
        用户登录，登录成功返回token，写将登录时间写入数据库；登录失败返回失败原因
        :param password:
        :return: json
        """
        adminInfo = Admin.query.filter_by(email=email).first()
        if (adminInfo is None):
            return jsonify(config.falseReturn('', '找不到用户'))
        else:
            if (adminInfo.password == password):
                login_time = int(time.time())
                adminInfo.update_time = login_time
                Admin.update(Admin)
                token = self.encode_auth_token(adminInfo.id, login_time)
                return jsonify(config.trueReturn(token.decode(), '登录成功'))
            else:
                return jsonify(config.falseReturn('', '密码不正确'))

    # 采用AES对称加密算法
    # str不是16的倍数那就补足为16的倍数
    @staticmethod
    def add_to_16(value):
        while len(value) % 16 != 0:
            value += '\0'
        return str.encode(value)  # 返回bytes

    def encrypt_oracle(self, text):
        # 初始化加密器
        aes = AES.new(self.add_to_16(config.SECRET_KEY), AES.MODE_ECB)
        # 先进行aes加密
        encrypt_aes = aes.encrypt(self.add_to_16(text))
        # 用base64转成字符串形式
        encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # 执行加密并转码返回bytes
        return encrypted_text

    def decrypt_oralce(self, text):
        # 初始化加密器
        aes = AES.new(self.add_to_16(config.SECRET_KEY), AES.MODE_ECB)
        # 优先逆向解密base64成bytes
        base64_decrypted = base64.decodebytes(text.encode(encoding='utf-8'))
        decrypted_text = str(aes.decrypt(base64_decrypted), encoding='utf-8')  # 执行解密密并转码返回str
        return decrypted_text
