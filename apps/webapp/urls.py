from dtlib import filetool
from apps.webapp.handlers import *

app_path = filetool.get_parent_folder_name(__file__)  # set the relative path in one place

url = [


    # todo: 这个后面不再用了,因为后面应用是和组织绑定了,谁拥有组织,谁就有应用的读写权限
    (r"/%s/get-auth-user-test-app/" % app_path, GetCurrentOrgTestApp),  # 获取当前用户的应用ID/KEY

    (r"/%s/get-org-test-apps/" % app_path, GetOrgTestApps),  # 获取当前用户的应用ID/KEY
]
