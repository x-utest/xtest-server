"""
这里面有类似于微信客户端扫码登录的全套解决方案。但是也有区别：

1. 本方法不是使用重定向，而是使用回调函数。所以不定型是登录，还可以用作为签名等场合。

"""
# from apps.auth2.handlers import *
# from dtlib import filetool
#
# app_path = filetool.get_parent_folder_name(__file__)  # set the relative path in one place
#
# url = [
#
#     # PC端的授权页面
#     (r"/%s/get-map-qrcode-token/" % app_path, GetMapQrCodeToken),  # PC上生成串，然后由客户端js生成qrcode，客户端生成二维码js只有10K
#
#     # 根据二维码授权结果，以字符形式的auth_token再换取第三方的access_token，
#     (r"/%s/get-auth-access-token/" % app_path, GetAuthAccessToken),
#
#     # 移动授权app客户端,手机端在扫码后，打开二维码所在页面
#     (r"/%s/app-confirm/" % app_path, AppConfirm),  # 这是二维码中的具体文字内容，手机端的确认
#
#     # 网站主服务器
#     (r"/%s/get-auth-user-info" % app_path, GetAuthUserInfo),
#
#     # todo 手机端注册
#     # . 输入邮箱，再轮询查看认证状态。
#     # . 输入手机号码，再发送验证码
#     # . 优先：直接绑定微信
#
#     # 创建开发平台auth应用
#     (r"/%s/create-auth-app/" % app_path, CreateAuthApp),
#
#     # 移动端数据安全
#     (r"/%s/up-ms-data/" % app_path, UploadMobileSafetyData),  # 获取手机风控数据，在登录的时候和手机放一起
#
#     # pc上面生成二维码,给手机扫描,由已经认证了的PC给手机进行授权--(这里面的功能给废弃掉)
#     # (r"/%s/get-pam-token-qrcode/" % app_path, GetPamTokenQrCode),  # PC上生成的二维码图片（1分钟刷新一次）,让手机扫描
#     # (r"/%s/get-mobile-token/" % app_path, GetMobileToken),  # 由手机发起的请求,获取和刷新access_token
#
#     # 由未授权PC上生成二维码,然后授权之后的手机扫码
#     # (r"/%s/get-map-token-qrcode/" % app_path, GetMapTokenQrCode),  # PC上生成的二维码图片（1分钟刷新一次）,让手机扫描（此种在服务端生成二维码的方案废弃掉）
#     # (r"/%s/pc-get-auth-result/" % app_path, PcGetAuthResult),  # PC端轮询获取授权的结果
#
#     # todo auth callback page的 CRUD
#     (r"/%s/create-auth-cb-page/" % app_path, CreateAuthCallbackPage),
#     # (r"/%s/get-auth-cb-page/" % app_path, GetAuthCallbackPage),
# ]

url = []
# 暂时注释掉, 似乎没用到 (2018-04-23)
