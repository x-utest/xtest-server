import os

from dtlib.tornado.base_hanlder import MyUserBaseHandler
from bson import ObjectId
from dtlib import jsontool
from dtlib.aio.base_mongo import wrap_default_rc_tag
from dtlib.aio.decos import my_async_paginator, my_async_jsonp
from dtlib.dtlog import dlog
from dtlib.tornado.base_hanlder import MyAppBaseHandler
from dtlib.tornado.decos import token_required, app_token_required
from dtlib.utils import list_have_none_mem
from dtlib.web.constcls import ConstData, ResCode
from dtlib.web.decos import deco_jsonp
from dtlib.web.tools import get_std_json_response
from dtlib.web.valuedict import ClientTypeDict
from dtlib.tornado.utils import get_org_data
from dtlib.tornado.utils import wrap_org_tag, wrap_project_tag, get_org_data_paginator


class ListApiTestData(MyUserBaseHandler):
    """
    前段页面显示出数据
    如果没有任何参数，则默认返回首页的n条数据
    如果并非首次回返
    --因为性能问题,取消使用 2016-09-30
    """

    @token_required()
    @my_async_jsonp
    @my_async_paginator
    async def get(self):
        pro_id = self.get_argument('pro_id', None)
        if pro_id is None:
            return await get_org_data(self, collection='api_test_data')
        else:
            return await get_org_data(self, collection='api_test_data', pro_id=pro_id)


class ListSafetyTestData(MyUserBaseHandler):
    """
    """

    @token_required()
    @my_async_jsonp
    @my_async_paginator
    async def get(self):
        return await get_org_data(self, collection='safety_test_report')


class ListApiReqDelay(MyUserBaseHandler):
    @token_required()
    @my_async_jsonp
    @my_async_paginator
    async def get(self):
        """
        查询所有的接口延时测试信息
        :return:
        """
        pro_id = self.get_argument('pro_id', None)
        if pro_id is None:
            return await get_org_data(self, collection='api_req_delay')
        else:
            return await get_org_data(self, collection='api_req_delay', pro_id=pro_id)
            # return await ApiReqDelay.objects.filter(project_name=project_name).order_by('rc_time',
            #                                                                             direction=DESCENDING).find_all()

            # return ApiReqDelay.objects.order_by('rc_time', direction=DESCENDING).find_all()


class ListPerformanceTestData(MyUserBaseHandler):
    """
    废弃掉的功能
    """

    @token_required()
    @my_async_jsonp
    @my_async_paginator
    async def get(self):
        return await get_org_data(self, collection='perform_report')


class ListUnitTestData(MyUserBaseHandler):
    """
    带分页的内容，不使用ORM了，这样返回会快速很多
    """

    @token_required()
    @my_async_jsonp
    async def get(self):
        """
        客户端将整个报告上传到服务器
        :return:返回插入的数据的id，方便后续做关联插入
        """
        pro_id = self.get_argument('pro_id', None)
        tag = self.get_arguments('tag')
        return await get_org_data_paginator(self, col_name='unit_test_data', pro_id=pro_id, hide_fields={'details': 0}, tag=tag)


class DeleteTestData(MyUserBaseHandler):
    """
    删除testdata（实际是将is_del设置为true）
    """

    @token_required()
    @my_async_jsonp
    async def get(self):
        id = self.get_argument('id', None)
        if id is None:
            return ConstData.msg_args_wrong

        # todo 做资源归属和权限的判断
        # project_obj = await .objects.get(id=ObjectId(str(id)))
        mongo_coon = self.get_async_mongo()
        mycol = mongo_coon['unit_test_data']
        pro_col = mongo_coon['test_project']
        testdata = await mycol.find_one({'_id': ObjectId(str(id))})
        testdata_organization = testdata['organization']
        user_org = await self.get_organization()

        if (testdata is None) or (testdata_organization is None):
            return ConstData.msg_forbidden

        pro_org_id = testdata_organization
        if pro_org_id != user_org:
            return ConstData.msg_forbidden

        await mycol.update_one({"_id": ObjectId(str(id))}, {"$set": {"is_del": True}})

        if 'tag' in testdata.keys():
            pro_id = testdata['pro_id']
            tag = testdata['tag']
            # todo: count records of this tag, if < 1, delete tag in project
            tags = await mycol.find({"pro_id": ObjectId(pro_id), 'is_del': False, 'tag': tag}, {'tag': 1}).count()
            if tags < 1:
                project = await pro_col.find_one({"_id": ObjectId(pro_id)})
                proj_tags = project['tags']
                proj_tags.remove(tag)
                await pro_col.update_one({"_id": ObjectId(pro_id)}, {"$set": {"tags": proj_tags}})
        return ConstData.msg_succeed


class CreateUnitTestData(MyAppBaseHandler):
    """
    插入测试数据,包括总值和明细值,高性能的一次性插入,没有用ORM
    """

    @app_token_required()
    # @my_async_jsonp
    async def post(self):
        """
        客户端将整个报告上传到服务器
        :return:
        """
        token = self.get_argument('token', None)
        req_dict = self.get_post_body_dict()

        # 做好字段的检查工作
        pro_id = req_dict.get('pro_id', None)
        failures = req_dict.get('failures', None)
        errors = req_dict.get('errors', None)
        details = req_dict.get('details', None)
        skipped = req_dict.get('skipped', None)
        pro_version = req_dict.get('pro_version', None)
        run_time = req_dict.get('run_time', None)
        total = req_dict.get('total', None)
        was_successful = req_dict.get('was_successful', None)
        tag = req_dict.get('tag', 'default')

        if list_have_none_mem(
                *[pro_id, failures, errors,
                  details, skipped,
                  pro_version, run_time,
                  total, was_successful, ]):
            return ConstData.msg_args_wrong

        if len(pro_version) > 32:  # 如果版本号长度大于32，比如出现了没有标定版本号的情况
            pro_version = '0.0.0.0.0'
            req_dict['pro_version'] = pro_version

        db = self.get_async_mongo()
        proj_col = db.test_project
        test_data_col = db.unit_test_data

        # project = await Project.objects.get(id=ObjectId(pro_id))
        project = await proj_col.find_one({'_id': ObjectId(pro_id)})
        """:type:Project"""

        app_org = await self.get_organization()
        """:type:Organization"""

        # if (project is None) or (project.organization is None):
        if project is None:
            return ConstData.msg_forbidden

        # 权限鉴定,不允许越权访问别人的组织的项目
        pro_org_id = project['organization']
        if pro_org_id != app_org:
            return ConstData.msg_forbidden

        # todo 后续的一些更细节的字段内在的约束检查

        req_dict = wrap_project_tag(req_dict, project)  # 加上项目标签
        req_dict = wrap_default_rc_tag(req_dict)  # 加上默认的标签
        req_dict = wrap_org_tag(req_dict, str(pro_org_id))  # 加上组织的标签
        insert_res = await test_data_col.insert_one(req_dict)
        insert_res = insert_res.inserted_id
        if 'tags' in project.keys():
            pro_tags = project['tags']
            # if tag in pro_tags:
            #     return ConstData.res_tpl % (ResCode.ok, 'success', '"' + str(insert_res) + '"')
        else:
            pro_tags = []
        if tag not in pro_tags:
            pro_tags.append(tag)
        await proj_col.update_one({'_id': ObjectId(pro_id)}, {'$set': {'tags': pro_tags}})
            # return ConstData.res_tpl % (ResCode.ok, 'success', '"' + str(insert_res) + '"')
        self.redirect('/share/get-utest-share-link/?token={}&rep_id={}'.format(token, insert_res))


class GetOneUnitTestData(MyUserBaseHandler):
    """
    获取一条记录
    """

    @token_required()
    @my_async_jsonp
    async def get(self):
        """
        要做鉴权和区分
        :return:
        """
        data_id = self.get_argument('id', None)
        if list_have_none_mem(*[data_id]):
            return ConstData.msg_args_wrong

        mongo_coon = self.get_async_mongo()
        mycol = mongo_coon['unit_test_data']

        user_org = await self.get_organization()
        """:type:Organization"""

        msg_details = await mycol.find_one({
            "organization": ObjectId(user_org),
            "_id": ObjectId(data_id)
        })

        return get_std_json_response(data=jsontool.dumps(msg_details, ensure_ascii=False))

class ApiAuth(MyAppBaseHandler):
    """
    验证API是否被授权了,通过ID和KEY来换取token
    """

    @my_async_jsonp
    async def post(self):
        appid = self.get_argument('appid_form', None)
        appkey = self.get_argument('appkey_form', None)

        if list_have_none_mem(*[appid, appkey]):
            return ConstData.msg_args_wrong

        db = self.get_async_mongo()
        app_col = db.test_data_app

        test_data_app = await app_col.find_one({'app_id': str(appid)})  # 后面要为app_id建立index
        if test_data_app is None:
            return ConstData.msg_none

        # 可以和数据库连接形成动态的验证
        if str(appkey) == str(test_data_app['app_key']):
            # todo:后面对于自动化的工具应用,要隔离部署,单独做一套体系,先默认使用某个人的信息了

            app_session = await self.create_app_session(app_id=appid, client_type=ClientTypeDict.api)

            if app_session is None:
                return ConstData.msg_forbidden

            # todo 后面要做高频的api接口的统计系统

            res_data = jsontool.dumps(app_session)
            dlog.debug(res_data)
            return get_std_json_response(data=res_data)
        else:
            return ConstData.msg_fail


class ApiAuthout(MyAppBaseHandler):
    """
    取消API和认证
    """

    @token_required()
    @deco_jsonp(is_async=False)
    def get(self):
        self.log_out()
        return get_std_json_response(code=200, msg='logout', data='')


# code trash (2018-04-23 yx)
# class CreatePerformReport(MyUserBaseHandler):
#     # TODO: change to motor
#     """
#     保存性能测试的数据指标
#     """
#
#     @token_required()
#     @my_async_jsonp
#     async def post(self):
#         # TODO 读取动态的内容
#         perform_report = PerformReport()
#         # data = json_decode(self.request.body)
#
#         # perform_report.server_soft_ware='squid/3.4.2'
#         perform_report.server_host_name = self.get_argument('doc_path', None)
#         perform_report.server_port = '80'
#         # perform_report.doc_path = '/'
#         # perform_report.doc_length = 131
#         perform_report.con_level = self.get_argument('con_level', None)  # 并发量
#         # perform_report.test_time_taken = 52.732 # 消耗时间 seconds
#         # perform_report.complete_req = data['con_level'] * 20  # 完成请求数
#         perform_report.failed_req = self.get_argument('failed_req', None)  # 失败请求数
#         # perform_report.non_2xx_res = IntField()#非2xx请求数
#         # perform_report.total_trans = 62505778#总传输数据量bytes
#         # perform_report.html_trans = 62472673#总html传输数据量bytes
#
#
#         perform_report.req_per_sec = self.get_argument('req_per_sec', None)  # 每秒请求量
#         perform_report.time_per_req = self.get_argument('time_per_req', None)  # 平均http请求响应时间
#         perform_report.time_per_req_across = self.get_argument('time_per_req_across', None)  # 平均事务响应时间
#         # perform_report.trans_rate = 1157.56#每秒传输数据量
#         # perform_report.time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         perform_report.set_default_rc_tag()
#
#         perform_report.organization = await self.get_organization()
#
#         perform_report.save()
#
#         return ConstData.msg_succeed
#
#
# class CreateSafetyTestReport(MyUserBaseHandler):
#     # TODO: change to motor
#     """
#     保存安全测试数据
#     """
#
#     @app_token_required()
#     @my_async_jsonp
#     async def get(self):
#         project_id = self.get_argument('project_id', None)
#         total_cnts = self.get_argument('total_cnts', None)
#         success_cnts = self.get_argument('success_cnts', None)
#         time_cycle = self.get_argument('time_cycle', None)
#         # project_name = self.get_argument('project_name', None)
#         hack_tool = self.get_argument('hack_tool', None)
#         notes = self.get_argument('notes', None)
#
#         if list_have_none_mem(*[project_id, total_cnts, success_cnts, time_cycle]) is True:
#             return ConstData.msg_args_wrong
#
#         # todo  判定项目从属的问题，后面要做成专门的公共函数
#         app_org = await self.get_org_by_app()
#         """:type:Organization"""
#         project = await Project.objects.get(id=ObjectId(project_id))
#         """:type:Project"""
#         if project is None or app_org is None:
#             return ConstData.msg_none
#         if app_org.get_id() != project.organization.get_id():
#             return ConstData.msg_forbidden
#
#         safety_report = SafetyTestReport()
#         safety_report.hack_tool = hack_tool
#         safety_report.total_cnts = int(total_cnts)
#         safety_report.success_cnts = int(success_cnts)
#         safety_report.success_rate = int(success_cnts) / int(total_cnts)
#         safety_report.time_cycle = float(time_cycle)
#         safety_report.crack_rate = float(time_cycle) / int(success_cnts)
#
#         safety_report.mark = notes  # 加上备注
#         safety_report.set_default_rc_tag()
#         await safety_report.set_project_tag(project)
#         await safety_report.save()
#
#         return ConstData.msg_succeed
#
#
# class CreateApiReqDelay(MyUserBaseHandler):
#     # TODO: change to motor
#     @app_token_required()
#     @my_async_jsonp
#     async def post(self):
#         """创建api访问的时间接口
#         """
#         pro_id = self.get_argument('pro_id', None)
#         domain = self.get_argument('domain', None)
#         path = self.get_argument('path', None)
#         delay = self.get_argument('delay', None)
#         http_status = self.get_argument('http_status', None)
#
#         if list_have_none_mem(*[domain, path, delay, pro_id, http_status]):
#             return ConstData.msg_args_wrong
#
#         project = await Project.objects.get(id=ObjectId(pro_id))
#         """:type:Project"""
#         if project is None:
#             return ConstData.msg_forbidden
#
#         api_req_delay = ApiReqDelay()
#         api_req_delay.project = project
#         api_req_delay.project_name = project.project_name
#         api_req_delay.domain = domain
#         api_req_delay.delay = delay
#         api_req_delay.path = path
#         api_req_delay.http_status = http_status
#         api_req_delay.organization = await self.get_org_by_app()
#         api_req_delay.set_default_rc_tag()
#
#         await api_req_delay.save()
#
#         return ConstData.msg_succeed
#
#
# class CreatePenetrationReport(MyUserBaseHandler):
#     # TODO: change to motor
#     """
#     渗透测试数据
#     """
#
#     @app_token_required()
#     @my_async_jsonp
#     async def post(self):
#         start_time = self.get_argument('start_time', None)
#         use_time = self.get_argument('use_time', None)
#         note = self.get_argument('note', None)
#         pro_id = self.get_argument('pro_id', None)
#         if list_have_none_mem(*[start_time, use_time]) is True:
#             return ConstData.msg_args_wrong
#
#         project = await Project.objects.get(id=ObjectId(pro_id))
#         """:type:Project"""
#
#         app_org = await self.get_org_by_app()
#         """:type:Organization"""
#
#         if (project is None) or (project.organization is None):
#             return ConstData.msg_forbidden
#
#         # 权限鉴定,不允许越权访问别人的组织
#         if project.organization.get_id() != app_org.get_id():
#             return ConstData.msg_forbidden
#
#         penetration_report = PenetrationTestData()
#         penetration_report.start_time = start_time
#         penetration_report.use_time = use_time
#         penetration_report.note = note
#         penetration_report.project = project
#         penetration_report.project_name = project.project_name
#         penetration_report.organization = project.organization
#         penetration_report.set_default_rc_tag()
#
#         result = await penetration_report.save()
#
#         res_str = get_std_json_response(code=200, data=jsontool.dumps(result.to_dict()))
#         return res_str
#
#
# class CreatePenetrationReportNote(MyUserBaseHandler):
#     # TODO: change to motor
#     """
#     渗透测试数据详情
#     """
#
#     @app_token_required()
#     @my_async_jsonp
#     async def post(self):
#         penetration_report = PenetrationTestDataNote()
#         penetration_report.penetration_id = self.get_argument('penetration_id', None)
#         penetration_report.ip = self.get_argument('ip', None)
#         penetration_report.details = self.get_argument('details', None)
#         # penetration_report.MongoEmptyPassword = self.get_argument('MongoEmptyPassword', None)
#         # penetration_report.RedisEmptyPassword = self.get_argument('RedisEmptyPassword', None)
#         # penetration_report.SSHRootEmptyPassword = self.get_argument('SSHRootEmptyPassword', None)
#         penetration_report.set_default_rc_tag()
#         penetration_report.organization = await self.get_org_by_app()
#         await penetration_report.save()
#
#         return ConstData.msg_succeed
#
#
# class CreateProxyipReport(MyUserBaseHandler):
#     # TODO: change to motor
#     """
#     代理测试数据
#     """
#
#     @app_token_required()
#     @my_async_jsonp
#     async def post(self):
#         proxyip_report = ProxyipTestData()
#         proxyip_report.remoteip = self.get_argument('remoteip', None)
#         proxyip_report.originalip = self.get_argument('originalip', None)
#         proxyip_report.proxyip = self.get_argument('proxyip', None)
#         proxyip_report.set_default_rc_tag()
#         proxyip_report.organization = await self.get_org_by_app()
#         await proxyip_report.save()
#
#         return ConstData.msg_succeed
#
#
# class ReadProxyipReport(MyUserBaseHandler):
#     """
#     读取代理测试数据
#     """
#
#     @token_required()
#     @my_async_jsonp
#     @my_async_paginator
#     async def get(self):
#         pro_id = self.get_argument('pro_id', None)
#         if pro_id is None:
#             return await get_org_data(self, collection='proxyip_test_data')
#         else:
#             return await get_org_data(self, collection='proxyip_test_data', pro_id=pro_id)
#
#
# class ReadPenetrationReport(MyUserBaseHandler):
#     """
#     读取渗透测试数据
#     """
#
#     @token_required()
#     @my_async_jsonp
#     @my_async_paginator
#     async def get(self):
#         pro_id = self.get_argument('pro_id', None)
#         if pro_id is None:
#             return await get_org_data(self, collection='penetration_test_data')
#         else:
#             return await get_org_data(self, collection='penetration_test_data', pro_id=pro_id)
#
#
# class ReadPenetrationReportNote(MyUserBaseHandler):
#     # TODO: change to motor
#     """
#     读取渗透测试数据详情
#     """
#
#     @token_required()
#     @my_async_jsonp
#     # @my_async_paginator
#     async def get(self):
#         penetration_id = self.get_argument('penetration_id', None)
#         res = await PenetrationTestDataNote.objects.filter(penetration_id=penetration_id).find_all()
#         result = []
#         for item in res:
#             result.append(item.to_dict())
#         data = get_std_json_response(code=200, data=jsontool.dumps(result))
#         return data
#
#
# class ReadDetailTestData(MyUserBaseHandler):
#     # TODO: change to motor
#     """
#
#     """
#
#     @token_required()
#     @my_async_jsonp
#     async def get(self):
#         id = self.get_argument('id', None)
#         callback = self.get_argument('callback', None)
#         res = await ApiTestDataNote.objects.filter(apitestdata_id=id).find_all()
#         result = []
#         for item in res:
#             result.append(item.to_dict())
#         data = get_std_json_response(code=200, data=jsontool.dumps(result))
#         return data
#
#
# class ReadTestDataTag(MyUserBaseHandler):
#     """
#     --因为性能问题,取消使用 2016-09-30
#     """
#
#     @token_required()
#     @my_async_jsonp
#     async def get(self):
#         id = self.get_argument('id', None)
#         res = await ApiTestData.objects.get(id=ObjectId(id))
#         return get_std_json_response(code=200, data=jsontool.dumps(res.to_dict()))
#
#
# class CreateFeedback(MyUserBaseHandler):
#     # TODO: change to motor
#     """
#     上传文件
#     """
#
#     @token_required()
#     @my_async_jsonp
#     async def post(self):
#         upload_path = os.path.join(os.path.dirname(__file__), 'files')  # 文件的暂存路径
#         file_metas = self.request.files['uploadfile']  # 提取表单中‘name’为‘file’的文件元数据
#         msg = self.get_argument('msg', None)
#         if list_have_none_mem(*[msg]):
#             return ConstData.msg_args_wrong
#
#         file_list = []
#         for meta in file_metas:
#             filename = meta['filename']
#             # filepath = os.path.join(upload_path, filename)
#             filepath = '/var/static/' + filename
#             with open(filepath, 'wb') as up:  # 有些文件需要已二进制的形式存储，实际中可以更改
#                 up.write(meta['body'])
#             file_list.append(filename)
#
#         feedback_msg = FeedbackMsg()
#         feedback_msg.msg = msg
#         feedback_msg.file_path = filepath
#         await feedback_msg.save()
#         return ConstData.msg_succeed
#
#
# class FeedbackList(MyUserBaseHandler):
#     """
#     查看列表
#     """
#
#     @token_required()
#     @my_async_jsonp
#     @my_async_paginator_list
#     async def get(self):
#         mongo_coon = self.get_async_mongo()
#
#         res = await mongo_coon['feedback_msg'].find({})
#         list = []
#         for i in res:
#             list.append(i.to_list())
#         return list
