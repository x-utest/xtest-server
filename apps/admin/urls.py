"""
运管和超管后台

主要包含的功能：

1. 注册用户的查看
2. 各种活动日志
"""
from apps.admin.handlers import *
from dtlib import filetool

app_path = filetool.get_parent_folder_name(__file__)  # set the relative path in one place

url = [

    # 用户信息
    # (r"/%s/get-all-user-info/" % app_path, ListUserInfo),  # 获取所有的注册用户的基本信息
    # (r"/%s/delete-user/" % app_path, DeleteUser),  # 删除用户
    # (r"/%s/online-user/" % app_path, OnlineUser),  # 在线用户
    # (r"/%s/get-user-counts/" % app_path, GetUserCounts),  # 获取注册用户的统计信息

    # 组织信息
    # (r"/%s/get-all-org-info/" % app_path,),  # 获取所有组织信息
    # (r"/%s/audit-org/" % app_path,),  # 审核组织
    # (r"/%s/freeze-org/" % app_path,),#冻结组织

    # (r"/%s/set-user-active-status/" % app_path, SetUserActiveStatus),  # 设置用户的激活状态
    #
    # # 接口调用
    # (r"/%s/read-api-call-counts/" % app_path, ListApiCallCount),  # api调用次数
    #
    # # 用户活动日志
    # (r"/%s/get-log-history/" % app_path, GetLogHistory),
    #
    # # 超级管理员全网用于监控的日志
    # (r"/%s/all-login-his/" % app_path, LoginHistory),  # 用户登录
    # (r"/%s/all-api-calls-his/" % app_path, ApiCallsHistory),  # 接口调用。非自动化的接口调用

    # 自动化的接口调用是高频的,要用单独的统计系统来部署
    (r"/%s/list-organization/" % app_path, ListOrganization),  # todo  分页列表,这个是所有的组织,属于管理人员的接口

    # 分三层权限控制
    # TODO 管理员用于监控自己企业的日志数据
    # todo 用户监控自己的日志数据

    (r"/%s/reset-admin-password/" % app_path, ResetAdminPassword),  # 使用 super_token 重置 admin 用户的密码
    (r"/%s/is-admin/" % app_path, IsAdmin),  # 是否是超级管理员
    (r"/%s/get-user-list/" % app_path, GetUserList),  # 获取用户列表
    (r"/%s/add-user/" % app_path, AddUser),  # 添加用户
    (r"/%s/delete-user/" % app_path, DeleteUser),  # 删除用户
    (r"/%s/lock-user/" % app_path, LockUser),  # 锁定用户
    (r"/%s/unlock-user/" % app_path, UnlockUser),  # 解锁用户
]
