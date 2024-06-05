import flask
import re
import base64

# 统一响应格式
class Resp:
    def __init__(self, status_code, data=None, msg=None):
        self.status_code = status_code
        self.data = data
        self.msg = msg

    def to_json(self):
        return flask.jsonify({
            'code': self.status_code,
            'msg': self.msg,
            'data': self.data,
        })

# 去除image base64头
def remove_image_b64_header(b64):
    return re.sub('^data:image/.+;base64,', '', b64)

def convert_bytes_to_base64(bytes_data):
    # 使用 base64 模块的 b64encode 函数将字节数据转换为 Base64 编码的字节数据
    base64_bytes = base64.b64encode(bytes_data)

    # 将字节数据转换为字符串并返回
    return base64_bytes.decode('utf-8')  # 返回解码后的字符串形式的 Base64 数据
