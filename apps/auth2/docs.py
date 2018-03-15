"""
本模块的所有内容都只针对于认证模块的app,
"""
from aiomotorengine import DateTimeField
from aiomotorengine import FloatField
from aiomotorengine import IntField
from aiomotorengine import ReferenceField
from aiomotorengine import StringField

from xt_base.document.auth2_docs import ProductResource
from xt_base.document.source_docs import OrgUserDataDocument
from dtlib.aio.base_mongo import HttpDocument, ClientTypeDocument, MyDocument
from dtlib.tornado.account_docs import User
from dtlib.utils import list_have_none_mem


class AuthUser(User):
    """
    目前先直接继承本用户体系的账号
    """
    __collection__ = "g_users"

# class EnterpriseAccount(User):
#     """
#     企业用户账号。
#     一个企业可以创建多个app应用
#     这些app应用共享用户池
#     """
#     __collection__ = 'auth_enterprise'


class AuthApp(OrgUserDataDocument, ClientTypeDocument):
    """
    开放应用程序,用于做身份认证的
    """

    __collection__ = "auth_app"
    __lazy__ = False

    appid = StringField(max_length=32, unique=True)  # 公钥
    secret = StringField(max_length=32, unique=True)  # 私钥
    callback = StringField()  # 可能是web回调的url或者是回调的app应用包名称,回调的域，用于安全性检查

    async def set_default_tag(self, **kwargs):
        """
        设置默认的标记
        :param kwargs:
        :return:
        """
        client_type = kwargs.get('client_type', None)
        http_req = kwargs.get('http_req', None)

        if list_have_none_mem(*[client_type, http_req]):
            return None

        await self.set_org_user_tag(http_req=http_req)
        self.set_client_type_tag(client_type=client_type)

        # super(AuthApp, self).set_default_rc_tag()
        return True


class ResourceGroup(MyDocument):
    """
    资源套餐组，不同的套餐组有不同的限额
    """
    __collection__ = 'resource_group'
    __lazy__ = False

    name = StringField()  # 小组名称


class OrgResourceGroupRelation(OrgUserDataDocument):
    """
    组织和资源组的关系，不同的资源组有不同的限额
    """

    __collection__ = 'org_resource_grp_rel'
    __lazy__ = False

    r_grp = ReferenceField(reference_document_type=ResourceGroup)
    rg_name = StringField()  # 冗余


class ResourceGroupLimit(OrgUserDataDocument):
    """
    每个账号的相应的资源的限额
    """

    __collection__ = 'resource_group_limit'
    __lazy__ = False

    resource = ReferenceField(reference_document_type=ProductResource)
    r_name = StringField()  # 冗余 ，资源名称
    limit = IntField()  # 目录创建的数目


class OrgResourceCnt(OrgUserDataDocument):
    """
    当前组织使用资源的情况
    """
    __collection__ = 'org_resource_cnt'
    __lazy__ = False

    resource = ReferenceField(reference_document_type=ProductResource)
    r_name = StringField()  # 冗余
    cnt = IntField()


# class UserPlatformApp(AuthApp):
#     """
#     用户开放平台应用,需要提供一些东西进行审核的
#     """
#
#     company_name = StringField(max_length=1024)  # 企业名称
#     website = StringField(max_length=1024)  # 企业网址
#     phone = StringField(max_length=32)  # 联系电话
#     status = IntField()  # 审核状态：0表示刚注册

#
# class WebOpenApp(AuthApp):
#     """
#     PC端的Web扫码登录App，对应的还有移动端的。
#     """
#     __collection__ = "auth_app"
#
#     cb_url = StringField(max_length=10240)  # 回调的url，类似于webhook一样，只要授权后，就调用的url


# class MobileOpenApp(AuthApp):
#     """
#     移动端开放平台app
#     """
#     __collection__ = "auth_mobile_app"
#     cb_app = StringField(max_length=10240)  # 回调的app应用包名称


# 正面都是系统数据，当然也有可能是业务数据

class MobileSafetyData(OrgUserDataDocument, HttpDocument,
                       # OperationDocument
                       ):
    """
    手机安全数据

    """

    __collection__ = 'mobile_safety_data'

    bs = StringField()  # charging battery status
    br = FloatField()  # 电池状态，"0.36",battery rate

    carrier = StringField()  # 运营商，"\U4e2d\U56fd\U8054\U901a";
    cellular = StringField()  # LTE;
    coun = StringField()  # CN;
    dn = StringField()  # "iPhone 6s"

    idf = StringField()  # 85BA4C903C16F7631;
    imei = StringField()  # 000000000000000;
    # ip = StringField()
    lang = StringField()  # "en-CN";
    sc_w = IntField()  # screen width
    sc_h = IntField()  # screen height
    # mScreen = StringField()  # 1242x2208;
    dType = StringField()  # iPhone;
    mac = StringField()  # "02:00:00:00";
    dModel = StringField()  # "iPhone8,2";
    osType = StringField()  # ios;
    # osVerInt =StringField()# "9.3.2";
    osVerRelease = StringField()  # "9.3.2";
    route = StringField()  # "24:3:b0";
    ssid = StringField()  # MyWIFI;
    # utc = StringField()  # "2016-07-18 06:51:53";
    uuid = StringField()  # "513DE79D-F20AB2F685A";

    c_time = DateTimeField()  # 客户端时间，东8时区

    # 下面是作为SDK时需要的字段
    # gsdkVerCode = "2.16.1.25.1.x";
    # hAppVerCode = 1;
    # hAppVerName = "1.0";
