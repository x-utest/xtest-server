# import pymongo
import motor
from dtlib.tornado.base_hanlder import MyUserBaseHandler
from bson import ObjectId
from dtlib import jsontool
from dtlib.aio.decos import my_async_jsonp
from dtlib.dtlog import dlog
from dtlib.randtool import get_uuid1_key
import hashlib
# from dtlib.tornado.account_docs import Organization, UserOrgRelation, User
from dtlib.tornado.decos import token_required
# from dtlib.tornado.docs import UserDetailInfo, UserRegInfo, FeedBackMsg
# from dtlib.tornado.status_cls import UserStatus, ResCode
# from dtlib.tornado.ttl_docs import WebToken, MobileToken, PcAuthMobileToken, AccessToken, TtlOrgInviteCode
from dtlib.utils import list_have_none_mem, get_rand_salt, hashlibmd5with_salt
from dtlib.web.constcls import ConstData
from dtlib.web.decos import deco_jsonp
from dtlib.web.tools import get_std_json_response
from dtlib.web.valuedict import ClientTypeDict

# from apps.account.docs import LanAppUser
from config import HTTP_PORT, mongodb_cfg, SERVER_PROCESS
# from config_api import capt_image_domain
# from xt_base.document.auth2_docs import MobileAuthPcToken
# from dtlib.tornado.utils import user_id_is_legal, create_dft_organization, create_org_app, create_dft_org_rel
import traceback

from dtlib.tornado.utils import set_default_rc_tag
from dtlib.tornado.status_cls import UserStatus, UserRegWay


class CheckEnv(MyUserBaseHandler):
    """
    检查环境
    """

    @my_async_jsonp
    async def get(self):
        tbl_out = {
            'http_port': HTTP_PORT,
            'process_num ': SERVER_PROCESS,
            'db_server': mongodb_cfg.host,
            'mongo_port': mongodb_cfg.port
        }
        try:
            con = motor.MotorCliento(host=mongodb_cfg.host, port=mongodb_cfg.port)
            db = con[mongodb_cfg.db_name]
            tbl_out['connect'] = True
            user_id = "admin"
            db = self.get_async_mongo()
            user_col = db.g_users
            res = await user_col.find_one({'user_id': user_id})
            if res:
                return ConstData.msg_exist
        except:
            traceback.print_exc()
            tbl_out['connect'] = "mongodb connect error"

        return get_std_json_response(data=jsontool.dumps(tbl_out, ensure_ascii=False))


class AccountInit(MyUserBaseHandler):
    @my_async_jsonp
    async def get(self):
        """
        初始化账号
        :return:
        """
        user_id = "admin"
        passwd = "admin@2018"
        u_name = 'your nickname'

        db = self.get_async_mongo()
        user_col = db.g_users
        user_reg_col = db.user_reg_info

        res = await user_col.find_one({'user_id': user_id})
        if res:
            return ConstData.msg_exist
        rand_salt = get_rand_salt()
        new_user = {
            'user_id': user_id,
            'salt': rand_salt,
            'nickname': u_name,
            'passwd': hashlibmd5with_salt(passwd, rand_salt)
        }
        new_user = set_default_rc_tag(new_user)
        new_user.update_one(self.set_template())
        user_res = await user_col.insert_one(new_user)
        user_res = user_res.inserted_id
        # new_user = await new_user.save()
        # """:type:User"""

        new_user_reg_info = {
            'user': user_res,
            'u_name': u_name
        }

        new_user_reg_info.update(self.set_http_tag())
        new_user_reg_info = set_default_rc_tag(new_user_reg_info)
        await user_reg_col.insert_one(new_user_reg_info)
        # await user_reg_info.save()

        org = await self.create_dft_organization(new_user_reg_info, is_default=True)
        await self.create_dft_org_rel(new_user_reg_info, org, is_default=False, is_current=True)
        res_dict = await self.create_org_app(org)
        res_dict['user'] = new_user['user_id']
        res_dict['password'] = passwd
        invite_json = jsontool.dumps(res_dict, ensure_ascii=False)
        return get_std_json_response(data=invite_json)

    @staticmethod
    def set_template():
        return dict(
            status=UserStatus.init,
            active=True,
            reg_way=UserRegWay.web
        )

    async def create_dft_organization(self, user, is_default=False):
        """
        创建默认的组织
        :type user: User
        :parameter is_default:是否是模板组织
        :return: 
        """
        # 为新用户建立默认的小组
        db = self.get_async_mongo()
        org_col = db.organization
        # default_org = Organization()

        new_org = dict(
            is_default=is_default,
            owner=user['user'],
            name = 'group template',  # 默认组织名称和用户昵称一样,后面提供修改接口
            home_page = 'http://www.my-org-page.org'
        )
        new_org = set_default_rc_tag(new_org)
        # default_org.owner_name = user.nickname  # 冗余
        org_id = await org_col.insert_one(new_org)
        org_id = org_id.inserted_id
        new_org['_id'] = org_id
        return new_org

    async def create_dft_org_rel(self, user, org,
                                 is_default=False,
                                 is_current=False,
                                 is_activate=True,
                                 is_owner=True
                                 ):
        """
        为组织和用户建立关联
        :param user: 
        :type user:User
        :type org:Organization
        :param org: 
        :return: 
        """
        # 建立它们的默认关系
        db = self.get_async_mongo()
        user_org_rel_col = db.user_org_rel

        new_rel = dict(
            organization=org['_id'],
            user=user['user'],
            is_default=is_default,
            is_current=is_current,
            is_owner=is_owner,
            is_active=is_activate
        )
        new_rel = set_default_rc_tag(new_rel)
        # user_org_rel.user_name = user.nickname  # 冗余
        return await user_org_rel_col.insert_one(new_rel)

    async def create_org_app(self, default_org):
        """
        为组织创建应用app
        :param default_org: 
        :type org:Organization
        :return: 
        """

        # default_test_app = TestDataApp()
        db = self.get_async_mongo()
        app_col = db.test_data_app
        new_app = dict(
            app_id=get_uuid1_key(),
            app_key=hashlib.md5(get_uuid1_key().encode(encoding='utf-8')).hexdigest(),
            organization=default_org['_id'],
            o_name=default_org['name'],
            is_default=True  # 是默认设置的
        )

        new_app = set_default_rc_tag(new_app)
        app_id = await app_col.insert_one(new_app)
        app_id = app_id.inserted_id
        new_app['_id'] = app_id
        return new_app


class GetAuthUserOrganization(MyUserBaseHandler):
    @token_required()
    @my_async_jsonp
    async def get(self):
        """
        用户当前视图下的组织信息
        :return:
        """
        res = await self.get_organization()
        db = self.get_async_mongo()
        org_col = db.organization
        org_res = await org_col.find_one({'_id': ObjectId(res)})
        return get_std_json_response(data=jsontool.dumps(org_res, ensure_ascii=False))


class UserLogin(MyUserBaseHandler):
    """
    用户登录,目前感觉还没有用到 2016-10-25
    todo: 后面在启用的时候,还需要继续fixbug
    """

    @deco_jsonp()
    async def post(self):

        post_dict = self.get_post_body_dict()
        user_id = post_dict.get(ConstData.user_form, None)
        passwd = post_dict.get(ConstData.passwd_form, None)

        if list_have_none_mem(*[user_id, passwd]):
            return ConstData.msg_args_wrong

        db = self.get_async_mongo()
        user_res = await db['g_users'].find_one({'user_id': user_id, 'is_del': False},
                                                {'_id': 1, 'passwd': 1, 'salt': 1, 'is_lock': 1})
        if not user_res:
            return ConstData.msg_fail

        try:
            if user_res['is_lock'] is True:
                return ConstData.msg_forbidden
        except:
            pass

        user_pass = user_res['passwd']
        user_salt = user_res['salt']
        _id = user_res['_id']

        md5_password = hashlibmd5with_salt(passwd, user_salt)

        # auth_res = await User.auth(user_id, passwd)
        if md5_password == user_pass:
            # if auth_res:
            token_res = await self.create_token_session(_id, client_type=ClientTypeDict.browser)
            data = {
                "token": token_res['token']
            }
            return get_std_json_response(msg="success", data=jsontool.dumps(data))
        else:
            return ConstData.msg_fail


class UserLogout(MyUserBaseHandler):
    """
    用户登录出，根据session来判断的,api，user,wechat都可以用这个
    """

    @token_required()
    @my_async_jsonp
    async def get(self):
        # 记录日志

        await self.log_out()

        return ConstData.msg_succeed


class SetAuthUserInfo(MyUserBaseHandler):
    """
    设置当前登录用户的信息,昵称,可以反复修改
    """

    @token_required()
    @my_async_jsonp
    async def post(self):
        req_dict = self.get_post_body_dict()
        # passwd = req_dict.get('passwd', None)
        nickname = req_dict.get('nick_name', None)

        if list_have_none_mem(*[nickname]):
            return ConstData.msg_args_wrong

        db = self.get_async_mongo()
        user_col = db.g_users

        current_auth_user = await user_col.find_one({'_id': self.cache_session['user']})

        current_auth_user['nickname'] = nickname
        await user_col.update_one({'_id': self.cache_session['user']},
                              {'$set': {'nickname': nickname}}, upsert=False)
        # current_auth_user = await current_auth_user.save()

        res_dict = dict(
            user_id=current_auth_user['user_id'],
            nickname=current_auth_user['nickname'],
            rc_time=current_auth_user['rc_time']
        )

        return get_std_json_response(data=jsontool.dumps(res_dict, ensure_ascii=False))


class GetAuthUserInfo(MyUserBaseHandler):
    """
    获取当前登录用户的信息
    """

    @token_required()
    @my_async_jsonp
    async def get(self):
        current_user_id = self.cache_session['user']
        # """:type:User"""

        mongo_conn = self.get_async_mongo()

        user_col = mongo_conn['g_users']

        current_auth_user = await user_col.find_one({'_id': ObjectId(current_user_id)})
        # print("user_col.find_one({'user_id': %s})" % current_user_id)

        if not current_auth_user:
            return ConstData.msg_fail

        res_dict = dict(
            user_id=current_auth_user["user_id"],
            nickname=current_auth_user["nickname"],
            rc_time=current_auth_user["rc_time"],
            # status=current_auth_user["status"],
        )

        res_data = jsontool.dumps(res_dict, ensure_ascii=False)
        dlog.debug(res_data)

        return get_std_json_response(data=res_data)


class UpdateUserDetailInfo(MyUserBaseHandler):
    @token_required()
    @my_async_jsonp
    async def post(self):
        """
        创建用户的详细信息，联系信息
        :return: 
        """

        post_body_dict = self.get_post_body_dict()

        qq = post_body_dict.get('qq', None)
        email = post_body_dict.get('email', None)
        phone = post_body_dict.get('phone', None)

        db = self.get_async_mongo()
        user_detail_col = db.user_detail_info

        user = self.get_current_session_user()
        user_detail_res = await user_detail_col.find_one({'user': user})
        user_detail = dict(
            qq=qq,
            email=email,
            phone=phone
        )
        if user_detail_res is None:  # 如果为空则创建一个
            user_col = db.g_users
            user_res = await user_col.find_one({'_id': user})
            new_user_detail = dict(
                user=user,
                u_name=user_res['nickname']
            )
            new_user_detail = set_default_rc_tag(new_user_detail)
            user_detail.update(new_user_detail)

        user_detail_col.update_one({'user': user}, {'$set': user_detail}, upsert=True)
        return ConstData.msg_succeed


class GetUserDetailInfo(MyUserBaseHandler):
    @token_required()
    @my_async_jsonp
    async def get(self):
        """
        获取用户的联系信息
        :return: 
        """

        db = self.get_async_mongo()
        user_col = db.user_detail_info
        user_detail = await user_col.find_one({'user': self.get_current_session_user()})

        if user_detail is None:  # 如果为空则创建一个
            user_detail = {}
        return get_std_json_response(data=jsontool.dumps(user_detail))

# class GetAuthUserAllOrganizations(MyUserBaseHandler):
#     # TODO: change to motor
#     @token_required()
#     @my_async_jsonp
#     async def get(self):
#         """
#         本用户的所有的组织信息
#         :return:
#         """
#         # user_id = self.get_user_id()
#         current_user = self.get_current_session_user()
#
#         if current_user is None:
#             return ConstData.msg_none
#
#         # 获取所有的组织关系
#         org_rels = await UserOrgRelation.objects.filter(user=current_user).find_all()
#         """:type:list[UserOrgRelation]"""
#
#         org_dict_list = []
#
#         for item in org_rels:
#             org = item.organization
#             """:type:Organization"""
#             org_dict = org.to_dict()
#             org_dict['is_current'] = item.is_current
#             org_dict_list.append(org_dict)
#
#         # res = await self.get_organization()
#         return get_std_json_response(data=jsontool.dumps(org_dict_list, ensure_ascii=False))

# region  Organization CRUBL

# class CreateDefaultOrganization(MyUserBaseHandler):
#     """
#     创建默认的模板Organization
#     """
#
#     @token_required()
#     @my_async_jsonp
#     async def get(self):
#         user = self.get_current_session_user()
#         org = await create_dft_organization(user)
#         await create_dft_org_rel(user, org, is_default=False, is_current=True)
#         res = await create_org_app(org)
#         invite_json = jsontool.dumps(res.to_dict(), ensure_ascii=False)
#         return get_std_json_response(data=invite_json)
#
#
# class CreateOrganization(MyUserBaseHandler):
#     # TODO: change to motor
#     """
#     创建Organization
#     """
#
#     async def post(self):
#         # 表单提取
#
#         name = self.get_argument("name", None)
#         home_page = self.get_argument("home_page", None)
#         # owner = self.get_argument("owner", None)
#
#         # 空值检查
#         if list_have_none_mem(*[name, home_page,
#                                 # owner,
#                                 ]):
#             return ConstData.msg_args_wrong
#
#         # 数据表赋值
#         doc_obj = Organization()
#
#         doc_obj.name = name
#         doc_obj.home_page = home_page
#         doc_obj.owner_id = self.cache_session.user_id
#         doc_obj.set_default_rc_tag()
#         await doc_obj.save()
#
#         return ConstData.msg_succeed
#
#
# class GetInviteCode(MyUserBaseHandler):
#     # TODO: change to motor
#     @token_required()
#     @my_async_jsonp
#     async def get(self):
#         """
#         生成邀请码
#         1. 查询ttl状态码
#         2. 如果没有则生成一条
#         3. 如果有则用原来的
#         #. 生成一条邀请链接
#         :return:
#         """
#         # 表单提取
#
#         org_id = self.get_argument("org_id", None)
#
#         # 空值检查
#         if list_have_none_mem(*[org_id,
#                                 ]):
#             return ConstData.msg_args_wrong
#
#         # 数据表赋值
#         org = await Organization.objects.get(id=ObjectId(str(org_id)))
#         """:type:Organization"""
#         invite_obj = await TtlOrgInviteCode.objects.get(organization=org)
#         """:type:TtlOrgInviteCode"""
#         if invite_obj is None:
#             new_invite = TtlOrgInviteCode()
#             new_invite.invite_code = get_uuid1_key()  # 生成一个邀请码
#             new_invite.organization = org
#             new_invite.o_name = org.name
#             new_invite.set_default_rc_tag()
#             await new_invite.save()
#             invite_json = jsontool.dumps(new_invite.to_dict(), ensure_ascii=False)
#             return get_std_json_response(data=invite_json)
#
#         invite_json = jsontool.dumps(invite_obj.to_dict(), ensure_ascii=False)
#         return get_std_json_response(data=invite_json)
#
#
# class GetOrgInviteLink(MyUserBaseHandler):
#     # TODO: change to motor
#     @token_required()
#     @my_async_jsonp
#     async def get(self):
#         """
#         生成邀请码
#         1. 查询ttl状态码
#         2. 如果没有则生成一条
#         3. 如果有则用原来的
#         #. 生成一条邀请链接
#         :return:
#         """
#         # 表单提取
#
#         # org_id = self.get_argument("org_id", None)
#
#         # 空值检查
#         # if list_have_none_mem(*[org_id,
#         #                         ]):
#         #     return ConstData.msg_args_wrong
#
#         # 数据表赋值
#         org = await self.get_organization()
#         """:type:Organization"""
#
#         # org = await Organization.objects.get(id=ObjectId(str(org_id)))
#
#         invite_obj = await TtlOrgInviteCode.objects.get(organization=org)
#         """:type:TtlOrgInviteCode"""
#         if invite_obj is None:
#             new_invite = TtlOrgInviteCode()
#             new_invite.invite_code = get_uuid1_key()  # 生成一个邀请码
#             new_invite.organization = org
#             new_invite.o_name = org.name
#             new_invite.set_default_rc_tag()
#             invite_obj = await new_invite.save()
#
#         invite_link = 'http://api.apiapp.cc/account/accept-org-invite-by-link/?invite_code=%s' \
#                       % invite_obj.invite_code
#
#         invite_dict = invite_obj.to_dict()
#         invite_dict['link'] = invite_link
#
#         invite_json = jsontool.dumps(invite_dict, ensure_ascii=False)
#         return get_std_json_response(data=invite_json)
#
#
# class AcceptOrgInviteByLink(MyUserBaseHandler):
#     # TODO: change to motor
#     @my_async_jsonp
#     async def get(self):
#         """
#         对于有cookie的用户，加入组织
#         :return:
#         """
#
#         log_session = await self.set_session_by_token(cookie_enable=True)
#
#         if log_session is None:
#             return ConstData.msg_unauthorized
#
#         # todo 后续完成一个新接口,对于有cookie的用户,可以直接通过打开链接的方式来加入到组织,
#         # 如果用户没有注册的话,就先让注册,会涉及专门的注册增长线路
#         invite_code = self.get_argument('invite_code', None)
#
#         if list_have_none_mem(*[invite_code, ]):
#             return ConstData.msg_args_wrong
#
#         invite_code_obj = await TtlOrgInviteCode.objects.get(invite_code=str(invite_code))
#         """":type:TtlOrgInviteCode"""
#
#         if invite_code_obj is None:
#             return ConstData.msg_none
#
#         # 根据要求建立此用户和组织之间的关系
#         current_user = self.get_current_session_user()
#         """:type:User"""
#
#         org = invite_code_obj.organization
#         """:type:Organization"""
#
#         # 如果已经有关系,就不需要建立关系了
#         new_user_org_rel = await UserOrgRelation.objects.get(user=current_user, organization=org)
#         """:type:UserOrgRelation"""
#
#         if new_user_org_rel is None:
#             # 新建组织关系
#             new_user_org_rel = UserOrgRelation()
#             new_user_org_rel.user = current_user
#             new_user_org_rel.user_name = current_user.nickname
#             new_user_org_rel.organization = org
#             new_user_org_rel.org_name = org.name
#             new_user_org_rel.is_current = False
#             new_user_org_rel.is_default = False
#             new_user_org_rel.is_owner = False
#             new_user_org_rel.is_active = True  # 未被审核的时候,就没被激活，早期为了进入系统便捷，便不需要审核
#             new_user_org_rel.set_default_rc_tag()
#             new_user_org_rel = await new_user_org_rel.save()
#             """:type:UserOrgRelation"""
#
#         # 到此处，可以保证有一个组织关系了，不管是旧的已经存在的还是新的
#
#         if new_user_org_rel.is_current:  # 如果这个组织就是当前组织
#             msg = '当前用户就在此邀请组织里面了'
#             return get_std_json_response(code=ResCode.ok, msg=msg)
#
#         # 如果用户不在邀请组织里面
#         new_user_org_rel.is_current = True
#
#         # 需要先将旧的is_current的组织状态去除
#         old_current_rels = await UserOrgRelation.objects.filter(user=current_user, is_current=True).find_all()
#         """:type:list[UserOrgRelation]"""
#         if len(old_current_rels) != 1:
#             msg = 'more than one current data,please contact the admin'
#             return get_std_json_response(code=403, msg=msg)
#
#         old_current_rel = old_current_rels[0]
#         old_current_rel.is_current = False
#
#         await new_user_org_rel.save()
#         await old_current_rel.save()
#
#         return ConstData.msg_succeed
#
#
# class ExitCurrentOrg(MyUserBaseHandler):
#     # TODO: change to motor
#     """
#     退出当前组织：
#     1. 删除自己和当前组织的关系（is_del置位）
#     2. 设置自己的当前组织为自己默认创建的组织
#     """
#
#     @token_required()
#     @my_async_jsonp
#     async def get(self):
#         current_user = self.get_current_session_user()
#         current_org = await self.get_organization()
#         """:type:Organization"""
#
#         user_org_rel = await UserOrgRelation.objects.get(
#             user=current_user,
#             organization=current_org,
#             is_current=True)
#         """:type:UserOrgRelation"""
#
#         assert user_org_rel is not None, '当前用户的组织信息不存在'
#
#         if user_org_rel.is_owner:
#             # 如果當前组织就是原始创建的组织，则不允许退出
#             msg = 'default org , can not exit'
#             return get_std_json_response(code=ResCode.forbidden, data={}, msg=msg)
#
#         user_org_rel.is_current = False  # 切换组织
#         user_org_rel.is_del = True  # 删除关系
#
#         dft_rel = await UserOrgRelation.objects.get(user=current_user, is_owner=True)
#         """:type:UserOrgRelation"""
#
#         dft_rel.is_current = True
#         dft_rel = await dft_rel.save()
#         await user_org_rel.save()
#
#         if dft_rel is None:
#             return ConstData.msg_fail
#
#         return ConstData.msg_succeed
#
#
# class InviteUserToOrg(MyUserBaseHandler):
#     # TODO: change to motor
#     """
#     邀请用户到Organization
#     """
#
#     @token_required()
#     @my_async_jsonp
#     async def get(self):
#         """
#         1. 根据传入的串和当前打开此串的用户token来建立关系
#         对于无cookie的用户可以使用此功能
#         :return:
#         """
#
#         # todo 后续完成一个新接口,对于有cookie的用户,可以直接通过打开链接的方式来加入到组织,如果用户没有注册的话,就先让注册,会涉及专门的注册增长线路
#         invite_code = self.get_argument('invite_code', None)
#
#         if list_have_none_mem(*[invite_code, ]):
#             return ConstData.msg_args_wrong
#
#         invite_code_obj = await TtlOrgInviteCode.objects.get(invite_code=str(invite_code))
#         """":type:TtlOrgInviteCode"""
#
#         if invite_code_obj is None:
#             return ConstData.msg_none
#
#         # 根据要求建立此用户和组织之间的关系
#         current_user = self.get_current_session_user()
#         """:type:User"""
#         org = invite_code_obj.organization
#         """:type:Organization"""
#
#         # 如果已经有关系,就不需要建立关系了
#         new_user_org_rel = await UserOrgRelation.objects.get(user=current_user, organization=org)
#         if new_user_org_rel is not None:
#             return ConstData.msg_exist
#
#         # 如果不存在,则建立关系。需要先将旧的is_current的组织状态去除
#         old_current_rels = await UserOrgRelation.objects.filter(user=current_user, is_current=True).find_all()
#         """:type:list[UserOrgRelation]"""
#         if len(old_current_rels) != 1:
#             msg = 'more than one current data,please contact the admin'
#             return get_std_json_response(code=403, msg=msg)
#
#         old_current_rel = old_current_rels[0]
#         old_current_rel.is_current = False
#
#         # 新建组织关系
#         new_user_org_rel = UserOrgRelation()
#         new_user_org_rel.user = current_user
#         new_user_org_rel.user_name = current_user.nickname
#         new_user_org_rel.organization = org
#         new_user_org_rel.org_name = org.name
#         new_user_org_rel.is_current = True
#         new_user_org_rel.is_default = False
#         new_user_org_rel.is_owner = False
#         new_user_org_rel.is_active = True  # 未被审核的时候,就没被激活，早期为了进入系统便捷，便不需要审核
#         new_user_org_rel.set_default_rc_tag()
#
#         await old_current_rel.save()
#         await new_user_org_rel.save()
#
#         return ConstData.msg_succeed
#
#
# class ReadOrganization(MyUserBaseHandler):
#     # TODO: change to motor
#     """
#     读取Organization
#     """
#
#     async def get(self):
#         callback = self.get_argument('callback', None)
#         res = await Organization.objects.filter().find_all()
#         result = []
#         for item in res:
#             result.append(item.to_dict())
#         data = get_std_json_response(code=200, data=jsontool.dumps(result))
#         data = '%s(%s)' % (callback, data)
#         self.write(data)
#
#
# class UpdateOrganization(MyUserBaseHandler):
#     # TODO: change to motor
#     """
#     更改Organization名称
#     """
#
#     @token_required()
#     @deco_jsonp()
#     async def post(self):
#         post_dict = self.get_post_body_dict()
#         id = post_dict.get('id', None)
#         name = post_dict.get('name', None)
#
#         if list_have_none_mem(*[id, name]):
#             return ConstData.msg_args_wrong
#
#         update_org = await Organization.objects.get(id=ObjectId(str(id)))
#
#         current_user = self.get_current_session_user()
#         if update_org.owner != current_user:
#             return ConstData.msg_forbidden
#
#         update_org.name = name
#         await update_org.save()
#         res_dict = dict(
#             data=update_org
#         )
#
#         return get_std_json_response(data=jsontool.dumps(res_dict, ensure_ascii=False))
#
#
# class DeleteOrganization(MyUserBaseHandler):
#     """
#     创建Organization
#     """
#
#     def get(self):
#         self.write('get')
#
#     def post(self):
#         self.write('post')
#
#
# class GetOrgMember(MyUserBaseHandler):
#     # TODO: change to motor
#     """
#     获取Organization中所有的成员，并显示激活状态
#     """
#
#     @token_required()
#     @deco_jsonp()
#     async def get(self):
#         org_id = self.get_argument('org_id', None)
#
#         if list_have_none_mem(*[org_id]):
#             return ConstData.msg_args_wrong
#
#         # cur_org = await Organization.objects.get(id=ObjectId(str(org_id)))
#         curr_org = await Organization.get_by_id(ObjectId(str(org_id)))
#         if curr_org is None:
#             return ConstData.msg_none
#
#         current_rels = await UserOrgRelation.objects.filter(organization=curr_org).find_all()
#         """:type:list[UserOrgRelation]"""
#
#         if len(current_rels) == 0:
#             return ConstData.msg_none
#
#         user_list = []
#         """:type:list[dict]"""
#
#         for current_rel in current_rels:
#             user = current_rel.user
#             """:type:User"""
#             user_dict = dict(
#                 user_id=user.user_id,
#                 name=user.nickname,
#                 is_active=current_rel.is_active
#             )
#             user_list.append(user_dict)
#
#         return get_std_json_response(data=jsontool.dumps(user_list, ensure_ascii=False))
#
#
# class AuditOrgMember(MyUserBaseHandler):
#     # TODO: change to motor
#     """
#     对用户加入组织的申请进行激活操作：确立有效的关系
#     """
#
#     @token_required()
#     @my_async_jsonp
#     async def get(self):
#         audit = self.get_argument('audit', None)  # 审核结果
#         rel_id = self.get_argument('rel_id', None)  # 需要审核的关系ID信息
#
#         if list_have_none_mem(*[audit, rel_id]):
#             return ConstData.msg_args_wrong
#
#         audit = True if audit == '1' else False
#
#         curr_org = await self.get_organization()
#         if curr_org is None:
#             return ConstData.msg_none
#
#         current_rels = await UserOrgRelation.objects.filter(
#             organization=curr_org,
#             id=ObjectId(str(rel_id))
#         ).find_all()
#         """:type:list[UserOrgRelation]"""
#
#         if len(current_rels) != 1:
#             return ConstData.msg_args_wrong
#
#         current_rel = current_rels[0]
#         current_rel.is_active = audit
#         await current_rel.save()
#
#         return ConstData.msg_succeed


# endregion


# code trash (2018-04-23)

# class CreateUser(MyUserBaseHandler):
#     # TODO: change to motor
#     """
#     注册用户
#     已启用管理员创建用户模式(2018-04-23)
#     """
#
#     @deco_jsonp()
#     async def post(self):
#
#         post_dict = self.get_post_body_dict()
#         user_id = post_dict.get(ConstData.user_form, None)
#         passwd = post_dict.get(ConstData.passwd_form, None)
#         u_name = post_dict.get('u_name', None)
#
#         if list_have_none_mem(*[user_id, passwd]):
#             return ConstData.msg_args_wrong
#
#         if u_name is None:
#             u_name = 'your nickname'
#
#         res = await User.is_exist(user_id)
#         if res is False:
#             return ConstData.msg_exist
#
#         rand_salt = get_rand_salt()
#         new_user = User()
#         new_user.user_id = user_id
#         new_user.salt = rand_salt
#         new_user.nickname = u_name
#         new_user.passwd = hashlibmd5with_salt(passwd, rand_salt)
#         new_user.set_default_rc_tag()
#         new_user.set_template()
#         new_user = await new_user.save()
#         """:type:User"""
#
#         user_reg_info = UserRegInfo()
#         user_reg_info.user = new_user
#         user_reg_info.u_name = new_user.nickname
#         user_reg_info.set_http_tag(http_req=self)
#         user_reg_info.set_default_rc_tag()
#         await user_reg_info.save()
#         return ConstData.msg_succeed
#
# class SetAuthUserPwd(MyUserBaseHandler):
#     # TODO: change to motor
#     """
#     设置当前登录用户的ID,只能修改一次
#     """
#
#     @token_required()
#     @my_async_jsonp
#     async def post(self):
#         req_dict = self.get_post_body_dict()
#         new_user_pwd = req_dict.get('new_pwd', None)
#         old_user_id = req_dict.get('old_pwd', None)
#
#         if list_have_none_mem(*[old_user_id, new_user_pwd]):
#             return ConstData.msg_args_wrong
#
#         # 做一些密码复杂性和合法性检查
#         if not user_id_is_legal(old_user_id):
#             return ConstData.msg_args_wrong
#
#         # 检查用户名是否已经存在
#         exist_user = await User.objects.get(user_id=old_user_id)
#         if exist_user is not None:
#             return ConstData.msg_exist
#
#         # 没有修改前,可以使用user_id来检查
#         current_auth_user = await User.objects.get(id=self.cache_session.user.get_id())
#         """:type:User"""
#         # mis_wechat_user = await MisWeChatUser.objects.get(user_id=self.cache_log_session.user_id)
#         # """:type:MisWeChatUser"""
#
#         # 非初始状态,不允许修改
#         if current_auth_user.status != UserStatus.init:
#             return ConstData.msg_forbidden
#
#         current_auth_user.user_id = old_user_id
#         current_auth_user.status = UserStatus.user_id_changed
#         current_auth_user = await current_auth_user.save()
#
#         # # 修改和微信相关联的信息
#         # mis_wechat_user.user_id = new_user_id
#         # await mis_wechat_user.save()
#
#         # 更新session里面的内容
#         old_session = await WebToken.objects.get(id=self.cache_session.get_id())
#         """:type:WebToken"""
#         old_session.user_id = old_user_id
#         await old_session.save()
#
#         res_dict = dict(
#             user_id=current_auth_user.user_id,
#             nickname=current_auth_user.nickname,
#             rc_time=current_auth_user.rc_time
#         )
#
#         return get_std_json_response(data=jsontool.dumps(res_dict, ensure_ascii=False))
#
#
# class SetAuthUserId(MyUserBaseHandler):
#     # TODO: change to motor
#     """
#     设置当前登录用户的ID,只能修改一次
#     """
#
#     @token_required()
#     @my_async_jsonp
#     async def post(self):
#         req_dict = self.get_post_body_dict()
#         new_user_id = req_dict.get('new_user_id', None)
#
#         if list_have_none_mem(*[new_user_id, ]):
#             return ConstData.msg_args_wrong
#
#         # 做一些密码复杂性和合法性检查
#         if not user_id_is_legal(new_user_id):
#             return ConstData.msg_args_wrong
#
#         # 检查用户名是否已经存在
#         exist_user = await User.objects.get(user_id=new_user_id)
#         if exist_user is not None:
#             return ConstData.msg_exist
#
#         # 没有修改前,可以使用user_id来检查
#         current_auth_user = await User.objects.get(id=self.cache_session.user.get_id())
#         """:type:User"""
#         # mis_wechat_user = await MisWeChatUser.objects.get(user_id=self.cache_log_session.user_id)
#         # """:type:MisWeChatUser"""
#
#         # 非初始状态,不允许修改
#         if current_auth_user.status != UserStatus.init.value:
#             return ConstData.msg_forbidden
#
#         current_auth_user.user_id = new_user_id
#         current_auth_user.status = UserStatus.user_id_changed.value
#         current_auth_user = await current_auth_user.save()
#
#         # # 修改和微信相关联的信息
#         # mis_wechat_user.user_id = new_user_id
#         # await mis_wechat_user.save()
#
#         # 更新session里面的内容
#         old_session = await WebToken.objects.get(id=self.cache_session.get_id())
#         """:type:WebToken"""
#         old_session.user_id = new_user_id
#         await old_session.save()
#
#         res_dict = dict(
#             user_id=current_auth_user.user_id,
#             nickname=current_auth_user.nickname,
#             rc_time=current_auth_user.rc_time
#         )
#
#         return get_std_json_response(data=jsontool.dumps(res_dict, ensure_ascii=False))
#
#
# class GetMobileToken(MyUserBaseHandler):
#     # TODO: change to motor
#     """
#     从PC引导到手机上,然后创建一个refresh_token
#
#     1. 如果不存在手机refresh_token,新增加一个,如果已经存在,则更新时间
#     2. 返回refresh_token给手机端,让手机来获取 access_token
#     3. 获取了 mobile_token 之后,表示pam_token已经被使用,则删除掉
#     """
#
#     @my_async_jsonp
#     async def get(self):
#         qrtoken = self.get_argument('qrtoken', None)
#         if qrtoken is None:
#             return ConstData.msg_args_wrong
#
#         pam_token = await PcAuthMobileToken.objects.get(token=qrtoken)
#         """:type:PcAuthMobileToken"""
#         if pam_token is None:
#             return ConstData.msg_anonymous
#
#         user = pam_token.user
#
#         mobile_token = await self.create_token_session(user, MobileToken,
#                                                        client_type=ClientTypeDict.mobile
#                                                        )
#         """:type:MobileToken"""
#
#         if mobile_token is not None:
#             await pam_token.complete_del()
#
#         return get_std_json_response(data=jsontool.dumps(mobile_token.to_dict()))
#
#
# class MobileAuthPc(MyUserBaseHandler):
#     # TODO: change to motor
#     """
#     登录的手机给PC授权
#     """
#
#     @token_required()
#     @my_async_jsonp
#     async def get(self):
#
#         qrtoken = self.get_argument('qrtoken', None)
#
#         user = self.get_current_session_user()  # 当前手机登录的用户
#
#         if qrtoken is None:
#             return ConstData.msg_args_wrong
#
#         map_token = await MobileAuthPcToken.objects.get(token=qrtoken)
#         """:type:MobileAuthPcToken"""
#
#         if map_token is None:
#             return ConstData.msg_none
#
#         # 授权,用户签名
#         map_token.user = user
#         map_token.user_id = user.user_id
#         map_token.u_name = user.nickname
#
#         await map_token.save()  # 成功签名后保存
#         return ConstData.msg_succeed


# class GetMobileAccessToken(MyUserBaseHandler):
#     # TODO: change to motor
#     """
#     通过 refresh_token 来获取 access_token
#
#     - 根据 refresh_token 获取 access_token
#     - 如果不存在,则建立移动端的 token
#     - 如果存在,则更新时间
#     - 不管是否存在,都会返回一个 access_token
#     """
#
#     @my_async_jsonp
#     async def get(self):
#         refresh_token = self.get_argument('rtoken', None)
#         if refresh_token is None:
#             return ConstData.msg_args_wrong
#
#         refresh_session = await MobileToken.objects.get(token=refresh_token)
#         """:type:MobileToken"""
#         if refresh_session is None:
#             return ConstData.msg_anonymous
#
#         user = refresh_session.user
#
#         acc_token = await self.create_token_session(user, AccessToken, client_type=ClientTypeDict.mobile)
#         """:type:AccessToken"""
#
#         return get_std_json_response(data=jsontool.dumps(acc_token.to_dict()))
#
#
# class LanApp(MyUserBaseHandler):
#     # TODO: change to motor
#     """
#     重定向到内网app
#     """
#
#     @token_required()
#     @my_async_jsonp
#     async def get(self):
#         token = self.get_token()
#         lan_user = await LanAppUser.objects.get(user=self.get_current_session_user())
#         """:type:LanAppUser"""
#         if lan_user is None:
#             lan_user = LanAppUser()
#             lan_user.is_active = False
#             lan_user.set_user_tag(http_req=self)
#             lan_user.set_default_rc_tag()
#             lan_user = await lan_user.save()
#
#         if not lan_user.is_active:
#             res_dict = dict(
#                 msg='请联系管理员激活内部用户使用权限'
#             )
#
#             std_res = get_std_json_response(data=jsontool.dumps(res_dict, ensure_ascii=False))
#
#             return std_res
#
#         lan_url = '%s/dist/index.html?token=%s' % (capt_image_domain, token)
#
#         res_dict = dict(
#             url=lan_url
#         )
#
#         std_res = get_std_json_response(data=jsontool.dumps(res_dict))
#         return std_res
#
#
# class Feedback(MyUserBaseHandler):
#     # TODO: change to motor
#     """
#     用户反馈信息
#     """
#
#     @token_required()
#     @my_async_jsonp
#     async def post(self):
#         body_dict = self.get_post_body_dict()
#         msg = body_dict.get('msg', None)
#
#         if list_have_none_mem(*[msg]):
#             return ConstData.msg_args_wrong
#
#         if len(msg) == 0:  # 如果是空字符串，也不允许
#             return ConstData.msg_args_wrong
#
#         feedback = FeedBackMsg()
#         feedback.msg = msg
#         feedback.label = 'improve'
#         feedback.set_user_tag(http_req=self)
#         feedback.set_default_rc_tag()
#         feedback.set_template()
#
#         await feedback.save()
#         return ConstData.msg_succeed
