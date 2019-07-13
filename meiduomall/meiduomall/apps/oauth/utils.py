from itsdangerous import TimedJSONWebSignatureSerializer

from meiduomall.settings import dev
from oauth import constants


def generate_access_token(openid):
    """
    签名 openid
    :param openid: 用户的 openid
    :return: access_token
    """

    # QQ 登录保存用户数据的token有效期
    # setting.SECRET_KEY:加密使用的密钥
    # SAVE_QQ_USER_TOKEN_EXPIRES = 600: 过期时间
    serializer = TimedJSONWebSignatureSerializer(dev.SECRET_KEY,
                                                 expires_in=constants.ACCESS_TOKEN_EXPIRES)
    data = {'openid': openid}
    token = serializer.dumps(data)
    return token.decode()
