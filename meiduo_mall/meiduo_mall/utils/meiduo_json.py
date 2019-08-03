import pickle
import base64


def dumps(json_dict):
    # 将字典转换成bytes
    json_bytes = pickle.dumps(json_dict)
    # 加密
    json_secret = base64.b64encode(json_bytes)
    # 转字符串
    json_str = json_secret.decode()

    return json_str


def loads(json_str):
    # 转bytes
    json_secret = json_str.encode()
    # 解密
    json_bytes = base64.b64decode(json_secret)
    # 转字典
    json_dict = pickle.loads(json_bytes)

    return json_dict
