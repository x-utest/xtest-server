"""
本服务特有的config，和标准的模板config独立出来
"""
BASE_DOMAIN = 'http://api.apiapp.cc'  # 根域名,一些全局变量里面会用到
QR_AUTH_DOMAIN = 'qrauth://api.apiapp.cc'  # 二维码用于扫码认证的
AUTH_CALLBACK_DOMAIN = 'http://xtest.apiapp.cc/'
capt_image_domain = 'http://192.168.1.200:8079'  # 本地打码图片服务器
