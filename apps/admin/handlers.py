from datetime import datetime

from dtlib import jsontool
from dtlib.aio.decos import my_async_jsonp
from dtlib.aio.decos import my_async_paginator
from dtlib.dtlog import dlog
from dtlib.timetool import get_current_utc_time
from dtlib.tornado.account_docs import MisWeChatUser, User
from dtlib.tornado.decos import token_required
from dtlib.tornado.docs import ApiCallCounts, LogHistory
from dtlib.tornado.ttl_docs import WebToken
from dtlib.utils import list_have_none_mem, hashlibmd5with_salt
from dtlib.web.constcls import ConstData
from dtlib.web.tools import get_std_json_response
from pymongo import DESCENDING

from apps.admin.decos import perm_check
from xt_base.base_server import MyBaseHandler
from xt_base.utils import get_org_data
from xt_base.utils import user_id_is_legal
from xt_base.document.acl_docs import UserGrpRel


class ListUserInfo(MyBaseHandler):
    """
    获取所有的用户的信息
    """

    @token_required()
    @my_async_jsonp
    @perm_check
    @my_async_paginator
    async def get(self):
        active = self.get_argument('active', None)

        if active is '1':
            return await User.objects.filter(active=True).order_by('rc_time', direction=DESCENDING).find_all()
        elif active is '0':
            return await User.objects.filter(active=False).order_by('rc_time', direction=DESCENDING).find_all()
        elif active is None:
            return await User.objects.order_by('rc_time', direction=DESCENDING).find_all()


class DeleteUser(MyBaseHandler):
    """
    删除用户
    """

    @token_required()
    @my_async_jsonp
    @perm_check
    async def get(self):
        user_id = self.get_argument("user_id", None)
        if user_id is None:
            return ConstData.msg_args_wrong
        res = await User.objects.filter(user_id=user_id).delete()
        await WebToken.objects.filter(user_id=user_id).delete()
        await MisWeChatUser.objects.filter(user_id=user_id).delete()
        return ConstData.msg_succeed


class OnlineUser(MyBaseHandler):
    """
    在线用户
    """

    @token_required()
    @my_async_jsonp
    @perm_check
    @my_async_paginator
    async def get(self):
        user = await WebToken.objects.find_all()
        user_id = []
        online_user = []
        for i in user:
            result = i.to_dict()
            user_id.append(result['user_id'])
        for x in user_id:
            user_detail = await User.objects.get(user_id=x)
            if user_detail is not None:
                online_user.append(user_detail)
            else:
                dlog.exception('login user is accidental deleted ')
        return online_user


class ListApiCallCount(MyBaseHandler):
    """
    read api调用次数
    """

    @token_required()
    @my_async_jsonp
    @perm_check
    @my_async_paginator
    async def get(self):
        return await ApiCallCounts.objects.order_by('counts', direction=DESCENDING).find_all()


class GetLogHistory(MyBaseHandler):
    """
    read api调用次数
    """

    @token_required()
    @my_async_jsonp
    @perm_check
    @my_async_paginator
    async def get(self):
        return await LogHistory.objects.order_by('rc_time', direction=DESCENDING).find_all()


class GetUserCounts(MyBaseHandler):
    @token_required()
    @my_async_jsonp
    async def get(self):
        """
        获取注册用户统计信息：
        1. 总体注册用户数
        2. 今日新增用户数
        :return:
        """
        col_name = 'g_users'
        mongo_coon = self.get_async_mongo()
        mycol = mongo_coon[col_name]

        total_cnts = await mycol.find().count()  # 总的用户数

        now_time = get_current_utc_time()
        start_time = datetime(now_time.year, now_time.month, now_time.day)  # 今日凌晨
        today_cnts = await mycol.find({'rc_time': {'$gte': start_time}}).count()  # 今日用户数

        res_dict = dict(
            total_cnt=total_cnts,
            today_cnt=today_cnts
        )

        return get_std_json_response(data=jsontool.dumps(res_dict, ensure_ascii=False))


class SetUserActiveStatus(MyBaseHandler):
    """
    设置用户激活信息
    1. 赋予默认组织
    2. 设置状态值
    """

    @token_required()
    @my_async_jsonp
    async def get(self):
        user_obj_id = self.get_argument('user_obj_id', None)
        is_set_active = self.get_argument('active', None)

        if list_have_none_mem(*[user_obj_id, is_set_active]) is True:
            return ConstData.msg_args_wrong

        user_info = await User.objects.get(user_id=user_obj_id)
        if is_set_active == '1':
            is_set_active = True
        elif is_set_active == '0':
            is_set_active = False
            await WebToken.objects.filter(user_id=user_obj_id).delete()

        if user_info is None:
            return ConstData.msg_none

        user_info.active = is_set_active
        await user_info.save()
        return ConstData.msg_succeed


class LoginHistory(MyBaseHandler):
    """
    人工调用接口的日志
    """

    @token_required()
    @my_async_jsonp
    @my_async_paginator
    async def get(self):
        """
        查询所有的接口延时测试信息
        :return:
        """
        return get_org_data(self, cls_name=LogHistory)


class ListOrganization(MyBaseHandler):
    """
    创建Organization
    """

    # todo

    def get(self):
        self.write('get')

    def post(self):
        self.write('post')


class ResetAdminPassword(MyBaseHandler):
    """
    重置 admin 用户的密码
    """

    @my_async_jsonp
    async def post(self):
        super_token = "3fb13a601c4111e8801f448a5b61a7f0bcb70841"
        req_dict = self.get_post_body_dict()
        new_user_pwd = req_dict.get('new_pwd', None)
        s_token_recv = req_dict.get('s_token', None)
        if list_have_none_mem(*[s_token_recv, new_user_pwd]):
            return ConstData.msg_args_wrong
        if super_token != s_token_recv:
            return ConstData.msg_forbidden
        # 做一些密码复杂性和合法性检查
        if not user_id_is_legal(new_user_pwd):
            return ConstData.msg_args_wrong
        old_session = await User.objects.get(user_id='admin')
        old_session.passwd = hashlibmd5with_salt(new_user_pwd, old_session.salt)
        await old_session.save()
        return ConstData.msg_succeed


class IsAdmin(MyBaseHandler):
    """
    是否是管理员
    """

    @token_required()
    @my_async_jsonp
    async def get(self):
        user = self.get_current_session_user()  # 获取当前用户
        grp_rel = await UserGrpRel.objects.get(user=user)
        """:type:UserGrpRel"""
        if grp_rel is None:
            res = dict(
                result=False
            )
            return get_std_json_response(data=jsontool.dumps(res))

        if grp_rel.g_name == 'admin':
            res = dict(
                result=True
            )
            return get_std_json_response(data=jsontool.dumps(res))
        else:
            res = dict(
                result=False
            )
            return get_std_json_response(data=jsontool.dumps(res))
