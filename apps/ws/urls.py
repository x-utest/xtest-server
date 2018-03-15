# coding:utf-8
"""
websocket相关接口
"""


from apps.ws.handlers import ApiTestsSocket
from dtlib import filetool

app_path = filetool.get_parent_folder_name(__file__)

url = [
    (r"/%s/exec-api-tests/" % app_path, ApiTestsSocket),  # 执行服务
]
