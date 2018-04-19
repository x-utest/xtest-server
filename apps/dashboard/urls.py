# coding:utf-8
"""
websocket相关接口
"""

from apps.dashboard.handlers import UpdateContent, GetContent, DeleteContent, UpdateProjectShow
from dtlib import filetool

app_path = filetool.get_parent_folder_name(__file__)

url = [
    (r"/%s/update_content/" % app_path, UpdateContent),  # 更新项目信息
    (r"/%s/delete_content/" % app_path, DeleteContent),  # 删除项目信息
    (r"/%s/get_content/" % app_path, GetContent),  # 获取项目信息
    (r"/%s/update_project_show/" % app_path, UpdateProjectShow),  # 更新展示状态
]
