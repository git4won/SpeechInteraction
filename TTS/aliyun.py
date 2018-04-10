# -*- coding: utf-8 -*-
# 阿里巴巴语音合成(TTS)测试
# 前提：注册开发者账号 && 实名认证 后创建[Access Key]。
#       [Access Key ID]和[Access Key Secret]是访问阿里云API的密钥。
#
# 参考：[语音合成REST接口](https://help.aliyun.com/document_detail/52793.html?spm=a2c4g.11186623.6.575.giqTBg)
# 使用：将申请到key填入代码中的的ak_id和ak_secret即可进行测试

import os
import datetime
import base64
import hmac
import md5
import hashlib
import tempfile
import json
import requests

import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)


def get_current_date():
    date = datetime.datetime.strftime(datetime.datetime.utcnow(), \
            "%a, %d %b %Y %H:%M:%S GMT")
    return date


def to_md5_base64(string):
    hash = hashlib.md5()
    hash.update(string)
    return hash.digest().encode('base64').strip()


def to_sha1_base64(string, secret):
    hmacsha1 = hmac.new(str(secret), str(string), hashlib.sha1)
    return base64.b64encode(hmacsha1.digest())


def get_speech(tts_string):
    config = {
            'ak_id': 'xxxxxxxxxxxxxxxx',
            'ak_secret': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    }

    options = {
            'url': 'http://nlsapi.aliyun.com/speak?encode_type=' + \
                    'wav&voice_name=' + 'xiaoyun' + '&volume=50',
            'method': 'POST',
            'body': tts_string.encode('utf-8'),
    }

    headers = {
            'date': get_current_date(),
            'content-type': 'text/plain',
            'authorization': '',
            # Accept Header需要允许audio和json两种返回格式。
            # 当语音合成成功（包括中途失败），服务器将返回在请求中要求的语音流。
            # 请求失败将返回json字符串。
            'accept': 'audio/wav, application/json'
    }

    # 调用阿里巴巴智能语音交互平台的任何功能前都需经过严格的鉴权验证。
    # 在处理用户请求前，服务端会校验Authorization Header以确保用户请求
    # 在传输过程中没有被恶意篡改或替换。
    # Authorization: Dataplus access_id:signature
    #
    # Authorization以固定字符串Dataplus开头，开发者需要将从阿里云
    # 申请到的access_id和经过计算的signature以:分隔并以Base64编码
    # 后加入Header。
    #
    # 与阿里云标准校验规范稍有不同，signature的计算需要首先对body
    # 内容进行MD5和Base64编码，然后将编码结果与 Method，Accept，
    # Content-Type和Date 合并产生特征值，最后用阿里云取得的access_key
    # 对特征值进行HMAC-SHA1加密生成signature。这里和标准方法的区别
    # 主要在于拼接特征值时不需要urlpath。

    # 1.对body进行MD5+BASE64加密
    body = options['body']
    bodymd5 = to_md5_base64(body)
    # 2.特征值
    feature = options['method'] + '\n' + headers['accept'] + '\n' + \
            bodymd5 + '\n' + headers['content-type'] + '\n' + headers['date']
    # 3. 对特征值HMAC-SHA1加密
    signature = to_sha1_base64(feature, config['ak_secret'])

    authHeader = 'Dataplus ' + config['ak_id'] + ':' + signature
    headers['authorization'] = authHeader

    url = options['url']
    r = requests.post(url, data=body, headers=headers, verify=False)
    # print headers
    # print r.status_code

    # 将语音文件保存到/tmp目录下
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
        f.write(r.content)
        tmpfile = f.name
        # print tmpfile

    return 0


if __name__ == '__main__':

    # 单次请求限制为300个UTF-8字符，即每个汉字、数字、字母都算一个字符。
    #text = '阿里云真不错'
    text = '请以UTF-8格式编码后将需要合成的语音文本在POST body中上传，单次请求限制为300个UTF-8字符，即每个汉字、数字、字母都算一个字符。'
    get_speech(text)


