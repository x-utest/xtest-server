from dtlib import filetool

from apps.share.handlers import *

app_path = filetool.get_parent_folder_name(__file__)  # 'apis'  # set the relative path in one place

url = [
    # 分享测试报告
    (r"/%s/get-utest-share-link/" % app_path, GetUtestShareLink),  # 获取Utest的分享链接
    (r"/%s/get-pro-share-link/" % app_path, GetProjectShareLink),  # 获取project的分享链接

    # 对分享的外链进行管理
    (r"/%s/my-utest-share/" % app_path, MyUtestShare),  # 我的Utest的分享链接
    (r"/%s/delete-utest-share/" % app_path, DeleteUtestShare),
    (r"/%s/update-utest-share/" % app_path, UpdateUtestShare),

    (r"/%s/my-project-share/" % app_path, MyProjectShare),  # 我的试项目报告的数据
    (r"/%s/update-project-share/" % app_path, UpdateProjectShare),
    (r"/%s/delete-project-share/" % app_path, DeleteProjectShare),  #

    # 通过stoken来获取数据的接口,不同的认证方式
    # todo 这块可以分离部署
    (r"/%s/get-utest-share-data/" % app_path, GetUtestShareData),  # 以分享途径获得测试报告的数据
    (r"/%s/get-pro-share-data/" % app_path, GetProjectShareData),  # 以分享途径获得测试项目报告的数据

]
