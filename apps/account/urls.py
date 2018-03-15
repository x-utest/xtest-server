from apps.account.handlers import *
from dtlib import filetool

app_path = filetool.get_parent_folder_name(__file__)  # set the relative path in one place

url = [
    # 用户注册登录
    (r"/%s/check-env/" % app_path, CheckEnv),
    (r"/%s/account-init/" % app_path, AccountInit),
    (r"/%s/create-new-user/" % app_path, CreateUser),  # 注册用户
    (r"/%s/user-login/" % app_path, UserLogin),  # 登入
    (r"/%s/user-logout/" % app_path, UserLogout),  # 登出

    # 用户信息操作
    (r"/%s/get-auth-user-info/" % app_path, GetAuthUserInfo),  # 获取当前登录的用户信息
    (r"/%s/set-auth-user-info/" % app_path, SetAuthUserInfo),  # 设置和修改当前登录的用户信息,可以反复修改
    (r"/%s/set-auth-user-id/" % app_path, SetAuthUserId),  # 修改用户ID,只能修改一次,取代默认生成的杂乱的ID
    (r"/%s/set-auth-user-pwd/" % app_path, SetAuthUserPwd),  # 设置用户密码

    (r"/%s/get-auth-user-org/" % app_path, GetAuthUserOrganization),  # 获取当前用户的当前视图下的组织信息
    (r"/%s/get-auth-user-all-orgs-info/" % app_path, GetAuthUserAllOrganizations),  # 获取当前登录的用户的所有的组织信息

    # 用户详细信息操作
    (r"/%s/update-user-detail/" % app_path, UpdateUserDetailInfo),  # 新增或者修改用户详细信息
    (r"/%s/get-user-detail/" % app_path, GetUserDetailInfo),  # 新增或者修改用户详细信息


    # 组织信息的操作
    # todo 后面权限要收回到组织管理员
    (r"/%s/create-organization/" % app_path, CreateOrganization),
    (r"/%s/create-default-organization/" % app_path, CreateDefaultOrganization),
    (r"/%s/read-organization/" % app_path, ReadOrganization),
    (r"/%s/update-organization/" % app_path, UpdateOrganization),  # 修改组织群
    (r"/%s/delete-organization/" % app_path, DeleteOrganization),
    (r"/%s/get-org-member/" % app_path, GetOrgMember),  # 获取组织成员
    (r"/%s/audit-org-member/" % app_path, AuditOrgMember),  # 审核用户加入组织的申请


    # 组织邀请机制
    # 复制邀请码产生的加入
    (r"/%s/get-invite-code/" % app_path, GetInviteCode),  # todo 后面要删除掉 获取邀请码,如果没有则创建一个
    (r"/%s/invite-user-to-org/" % app_path, InviteUserToOrg),  # todo 后面要删除掉 点击此链接,就可以加入此组织
    # 在PC上点击链接产生的邀请
    (r"/%s/get-org-invite-link/" % app_path, GetOrgInviteLink),  # 点击此链接,就可以加入此组织
    (r"/%s/accept-org-invite-by-link/" % app_path, AcceptOrgInviteByLink),  # 直接打开链接加入组织
    (r"/%s/exit-current-org/" % app_path, ExitCurrentOrg),  # 退出当前组织，返回到自己的默认组织
    # todo 通过手机扫描二维码产生的邀请加入

    # 移动端
    # (r"/%s/mobile-auth-pc-login/" % app_path, MobileAuthPc),  # 由手机扫码,对此token签名授权
    (r"/%s/get-mobile-access-token/" % app_path, GetMobileAccessToken),  # 由refresh_token获取access_token

    # 其它接口
    (r"/%s/lan-app/" % app_path, LanApp),  # 重定向到内网app

    (r"/%s/feedback/" % app_path, Feedback),  # 登录用户提交反馈信息

]
