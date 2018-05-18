# 这个要移到第三方
from asyncio import sleep
from dtlib import jsontool
from dtlib.aio.decos import my_async_jsonp
from dtlib.randtool import get_uuid1_key, generate_rand_id
from dtlib.timetool import convert_default_str_to_dt_time
from dtlib.tornado.decos import token_required
from dtlib.tornado.ttl_docs import WebToken
from dtlib.utils import list_have_none_mem
from dtlib.web.constcls import ConstData, QrAuthStatusCode
from dtlib.web.tools import get_std_json_response
from dtlib.web.valuedict import ClientTypeDict

from apps.auth2.decos import async_auth_access_token_required
from config_api import QR_AUTH_DOMAIN, BASE_DOMAIN, AUTH_CALLBACK_DOMAIN
from dtlib.tornado.base_hanlder import MyUserBaseHandler

# from xt_base.document.auth2_docs import ThirdAuthToken, MobileAuthPcToken, AuthAccessToken, \
#     MobileSafetyData, AuthApp
# from xt_base.document.source_docs import AuthCallbackPage

try:
    from xt_wechat.config import my_auth_app
except:
    print("Wechat module didn't installed!")


# TODO: 后面有需要重写相关功能


class GetMapQrCodeToken(MyUserBaseHandler):
    """
    PC端将文本内容返回给客户端，由客户端生成二维码

    客户端定时请求,每次请求都会导致code发生变化
    """

    @my_async_jsonp
    async def get(self):
        appid = self.get_argument('appid', None)

        if list_have_none_mem(*[appid]):
            return ConstData.msg_args_wrong

        # todo 后续要加一次数据库IO来查询是否存在此qrcode
        unauth_token = await self.create_anonymous_token(
            MobileAuthPcToken,
            appid=appid,
            client_type=ClientTypeDict.browser
        )
        """:type:MobileAuthPcToken"""

        # 这个链接是给手机打开的,用来给PC签名授权
        url = '%s/auth2/app-confirm/' % QR_AUTH_DOMAIN

        res_dict = dict(
            appid=appid,
            url=url,
            qrtoken=unauth_token.token
        )
        res_data = get_std_json_response(data=jsontool.dumps(res_dict))
        return res_data


class AppConfirm(MyUserBaseHandler):
    """
    手机端扫码后相应的状态提醒。
    如果扫码了，则调出确认的页面，扫码时也改变状态值为410：
    1. 如果确认或者取消后，则使用access_token和uuid去修改状态（注意检查资源从属问题）
    #. 如果确认登录后，就进行签名，而且修改状态值为200
    """

    @token_required()
    @my_async_jsonp
    async def get(self):
        uuid = self.get_argument('uuid', None)
        confirm = self.get_argument('confirm', None)

        if list_have_none_mem(*[uuid, ]):
            return ConstData.msg_args_wrong

        current_auth_token = await  MobileAuthPcToken.objects.get(token=uuid)
        """:type:MobileAuthPcToken"""

        if current_auth_token is None:
            return ConstData.msg_forbidden

        user = self.get_current_session_user()  # 当前手机登录的用户

        if confirm is None:
            current_auth_token.status = QrAuthStatusCode.wait
        elif confirm == '1':
            # 将状态修改为 确认授权态,授权,用户签名
            current_auth_token.user = user
            current_auth_token.user_id = user.user_id
            current_auth_token.u_name = user.nickname
            current_auth_token.status = QrAuthStatusCode.confirm

            # 然后创建auth_token，这个会告诉PC端此用户已经登录，然后把此session传给PC端
            # 直接创建webtoken,暂先不客auth_token
            await self.create_token_session(user,
                                            WebToken,
                                            client_type=ClientTypeDict.browser
                                            )  # 创建一个PC端的access_token
        else:
            # 将状态修改为 取消授权态
            current_auth_token.status = QrAuthStatusCode.cancel

        current_auth_token = await current_auth_token.save()

        return get_std_json_response(data=jsontool.dumps(current_auth_token.to_dict()))


# region 以下就是PC端后续的调用接口

class GetAuthAccessToken(MyUserBaseHandler):
    """
    auth2.0里面的获取认证信息，因为二维码信息容易被获取，所以中间再加一个auth_token
    ：需要私钥(影子）。此时是可信的服务器作为通讯双方
    """

    @my_async_jsonp
    async def get(self):
        appid = self.get_argument('appid', None)  # 应用公钥
        shadow_secret = self.get_argument('shadow_secret', None)  # 影子私钥
        auth_token = self.get_argument('auth_token', None)  # 用户授权token

        if list_have_none_mem(*[appid, shadow_secret, auth_token]):
            return ConstData.msg_args_wrong

        auth_token = await ThirdAuthToken.objects.get(token=auth_token)
        """:type:ThirdAuthToken"""
        if auth_token is None:
            return ConstData.msg_none

        access_token = await AuthAccessToken.objects.get(user=auth_token.user)
        """:type:AuthAccessToken"""

        res_data = get_std_json_response(data=jsontool.dumps(access_token.to_dict()))
        return res_data


class GetAuthUserInfo(MyUserBaseHandler):
    """
    另外的一套独立的token体系，后面会独立出来
    """

    @async_auth_access_token_required
    async def get(self):
        """
        返回信息里面有用户针对此应用的unionid信息，方便第三方应用系统A做好账号映射工作
        :return:
        """
        await sleep()


class UploadMobileSafetyData(MyUserBaseHandler):
    """
    获取手机风控相关数据
    """

    @token_required()
    @my_async_jsonp
    async def post(self):
        mobile_safety_data = self.get_post_body_dict()

        if mobile_safety_data is None:
            return ConstData.msg_args_wrong

        print(jsontool.dumps(mobile_safety_data))

        # operation_key = mobile_safety_data.get('op', None)  # operation 桩，整数：0，1，2，3
        mobile_info = mobile_safety_data.get('mi', None)  # 收集的手机静态信息,mobile info
        apps_info = mobile_safety_data.get('ai', None)  # 安装的应用信息, apps info
        client_time_str = mobile_safety_data.get('tm', None)  # time
        # todo 后面存储应用的数据信息

        # operation_dict = OperationDict.get_value_by_attrib_name(operation_key)

        if list_have_none_mem(*[mobile_info, apps_info, client_time_str,
                                # operation_dict
                                ]):
            return ConstData.msg_args_wrong

        ms_data = MobileSafetyData()
        ms_data.bs = mobile_info.get('bs', None)

        # 电池电量
        battery_rate = mobile_info.get('br', None)
        if battery_rate is not None:
            ms_data.br = float(battery_rate)

        ms_data.carrier = mobile_info.get('carrier', None)
        ms_data.cellular = mobile_info.get('cellular', None)
        ms_data.coun = mobile_info.get('coun', None)
        ms_data.dn = mobile_info.get('dn', None)
        ms_data.idf = mobile_info.get('idf', None)
        ms_data.imei = mobile_info.get('imei', None)
        ms_data.lang = mobile_info.get('lang', None)

        # 屏幕分辨率
        screen_width = mobile_info.get('dw', None)
        screen_height = mobile_info.get('dh', None)
        if not list_have_none_mem(*[screen_height, screen_width]):
            ms_data.sc_h = int(screen_height)
            ms_data.sc_w = int(screen_width)

        ms_data.dType = mobile_info.get('dType', None)
        ms_data.mac = mobile_info.get('mac', None)
        ms_data.dModel = mobile_info.get('dModel', None)
        ms_data.osType = mobile_info.get('osType', None)
        ms_data.osVerRelease = mobile_info.get('osVerRelease', None)
        ms_data.route = mobile_info.get('route', None)
        ms_data.ssid = mobile_info.get('ssid', None)
        ms_data.uuid = mobile_info.get('uuid', None)

        client_time = convert_default_str_to_dt_time(client_time_str)
        ms_data.c_time = client_time

        # 设置组织和人员归属关系
        await ms_data.set_org_user_tag(http_req=self)
        ms_data.set_http_tag(http_req=self)
        # 设置操作类型
        # ms_data.set_operation_tag(operation_dict)

        await ms_data.save()

        return ConstData.msg_succeed


class CreateAuthApp(MyUserBaseHandler):
    """
    建议auth应用
    """

    @token_required()
    @my_async_jsonp
    async def get(self):
        client_name = self.get_argument('client', None)
        if client_name is None:
            return ConstData.msg_args_wrong

        client_type = ClientTypeDict.get_value_by_attrib_name(client_name)
        if client_type is None:
            return ConstData.msg_args_wrong

        auth_app = AuthApp()

        uuid_key = get_uuid1_key()

        auth_app.appid = uuid_key
        auth_app.secret = generate_rand_id(sstr=uuid_key)
        auth_app.callback = BASE_DOMAIN

        await auth_app.set_default_tag(client_type=client_type, http_req=self)
        await  auth_app.save()

        return ConstData.msg_succeed


# endregion


class CreateAuthCallbackPage(MyUserBaseHandler):
    """
    创建page
    """

    @token_required()
    @my_async_jsonp
    async def get(self):
        auth_cb_page = AuthCallbackPage()
        auth_cb_page.url = AUTH_CALLBACK_DOMAIN
        await auth_cb_page.set_org_user_tag(http_req=self)
        auth_cb_page.set_template()
        auth_cb_page.set_default_rc_tag()
        await auth_cb_page.save()
        return ConstData.msg_succeed
