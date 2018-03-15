"""
任何一个Web系统里面都需要的一些提供系统信息的工具集
"""
from apps.base.handlers import *
from dtlib import filetool

app_path = filetool.get_parent_folder_name(__file__)  # set the relative path in one place

url = [
    # 公用
    (r"/", MainHandler),
    (r"/app-info/", AppInfo),
    (r"/private-app-info/", PrivateAppInfo),  # 一些隐私一些的应用信息

    (r"/get-client-info/", GetClientInfo),  # 获取客户端请求信息，包括IP地址
    (r"/create-server-asset/", CreateServerAsset),  # 创建信息服务器资产
]
