import math

import pymongo
from xt_base.base_server import MyBaseHandler
from bson import ObjectId
from dtlib import jsontool
from dtlib.randtool import generate_uuid_token
from dtlib.tornado.decos import token_required
from dtlib.utils import list_have_none_mem
from dtlib.web.constcls import ConstData
from dtlib.web.decos import deco_jsonp
from dtlib.web.tools import get_std_json_response

from apps.share.docs import ShareTestReport, ShareProjectReport
from xt_base.document.testdata_docs import UnitTestData
from xt_base.document.base_docs import Project
from xt_base.utils import get_org_data_paginator

share_page = '/utest-report-share.html?stoken='  # 单独部署的一套前端内容

pro_share_page = '/pro-report-share.html?stoken='  # 单独部署的一套前端内容


class GetUtestShareLink(MyBaseHandler):
    """
    获取分享链接 
    """

    @token_required()
    @deco_jsonp()
    async def get(self):
        """
        1. 自己当前的组织下的资源
        2. 生成share的内容
        
        支持手机端的
        :return: 
        """

        rep_id = self.get_argument('rep_id', None)  # 测试报告的ID

        if list_have_none_mem(*[rep_id]):
            return ConstData.msg_args_wrong

        # todo 做资源归属和权限的判断
        test_data = await UnitTestData.objects.get(id=ObjectId(rep_id))
        user_org = await self.get_organization()
        project = await Project.objects.get(id=ObjectId(test_data.pro_id))

        if (project is None) or (project.organization is None):
            return ConstData.msg_forbidden

        pro_org_id = project.organization.get_id()
        if pro_org_id != user_org.get_id():
            return ConstData.msg_forbidden

        share_obj = await ShareTestReport.objects.get(rep_id=rep_id)

        if share_obj is None:  # 如果不存在分享Link则创建一组
            stoken = generate_uuid_token()  # 生成一组随机串，分享的时候会看到

            share_obj = ShareTestReport()
            share_obj.rep_id = rep_id
            share_obj.stoken = stoken
            await share_obj.set_project_tag(project)

            share_obj.cnt = 0
            # share_obj.set_default_rc_tag()
            await share_obj.set_org_user_tag(http_req=self)
            share_obj = await share_obj.save()

        # 如果有，则直接使用
        share_url = share_page + share_obj.stoken

        res_dict = dict(
            share_url=share_url
        )

        return get_std_json_response(data=jsontool.dumps(res_dict))


class GetUtestShareData(MyBaseHandler):
    """
    获取分享的单元测试数据接口
    """

    @deco_jsonp()
    async def get(self):
        stoken = self.get_argument('stoken', None)

        if list_have_none_mem(*[stoken]):
            return ConstData.msg_args_wrong

        share_obj = await ShareTestReport.objects.get(stoken=stoken)

        if share_obj is None:
            return ConstData.msg_forbidden

        # todo 把完整的Unittest的报告内容获取出来并返回
        # res = await UnitTestData.objects.get(id=ObjectId(share_obj.rep_id))

        mongo_coon = self.get_async_mongo()
        mycol = mongo_coon['unit_test_data']
        msg_details = mycol.find({"_id": ObjectId(str(share_obj.rep_id))})
        msg_content_list = await msg_details.to_list(1)

        msg_content = msg_content_list[0]

        # 做一个阅读访问次数的计数
        if share_obj.cnt is None:
            share_obj.cnt = 0
        share_obj.cnt += 1
        await share_obj.save()

        return get_std_json_response(data=jsontool.dumps(msg_content, ensure_ascii=False))


class GetProjectShareLink(MyBaseHandler):
    """
    获取项目成长分享链接
    """

    @token_required()
    @deco_jsonp()
    async def get(self):
        """
        1. 自己当前的组织下的资源
        2. 生成share的内容

        支持手机端的
        :return:
        """

        pro_id = self.get_argument('project_id', None)  # 测试报项目的ID

        if list_have_none_mem(*[pro_id]):
            return ConstData.msg_args_wrong

        # todo 做资源归属和权限的判断

        user_org = await self.get_organization()
        project = await Project.objects.get(id=ObjectId(str(pro_id)))

        if (project is None) or (project.organization is None):
            return ConstData.msg_forbidden

        pro_org_id = project.organization.get_id()
        if pro_org_id != user_org.get_id():
            return ConstData.msg_forbidden

        share_obj = await ShareProjectReport.objects.get(pro_id=pro_id)

        if share_obj is None:  # 如果不存在分享Link则创建一组
            stoken = generate_uuid_token()  # 生成一组随机串，分享的时候会看到

            share_obj = ShareProjectReport()
            share_obj.pro_id = pro_id
            share_obj.stoken = stoken
            share_obj.cnt = 0
            await share_obj.set_project_tag(project)
            # share_obj.set_default_rc_tag()
            await share_obj.set_org_user_tag(http_req=self)
            share_obj = await share_obj.save()

        # 如果有，则直接使用
        share_url = pro_share_page + share_obj.stoken

        res_dict = dict(
            share_url=share_url
        )

        return get_std_json_response(data=jsontool.dumps(res_dict))


class GetProjectShareData(MyBaseHandler):
    """
    获取分享的单元测试数据接口
    """

    @deco_jsonp()
    async def get(self):
        stoken = self.get_argument('stoken', None)
        if list_have_none_mem(*[stoken]):
            return ConstData.msg_args_wrong

        page_size = self.get_argument('page_size', 30)
        page_idx = self.get_argument('page_idx', 1)
        page_size = int(page_size)
        page_idx = int(page_idx)

        share_obj = await ShareProjectReport.objects.get(stoken=stoken)

        if share_obj is None:
            return ConstData.msg_forbidden

        # todo 把完整的Unittest的报告内容获取出来并返回
        # res = await UnitTestData.objects.get(id=ObjectId(share_obj.rep_id))

        # 做一个阅读访问次数的计数
        if share_obj.cnt is None:
            share_obj.cnt = 0
        share_obj.cnt += 1
        await share_obj.save()

        mongo_coon = self.get_async_mongo()
        mycol = mongo_coon['unit_test_data']
        res = mycol.find({"pro_id": ObjectId(str(share_obj.pro_id))}, {"details": 0},
                         sort=[('rc_time', pymongo.DESCENDING)])

        page_count = await res.count()
        msg_details = res.skip(page_size * (page_idx - 1)).limit(page_size)  # 进行分页

        total_page = math.ceil(page_count / page_size)  # 总的页面数

        msg_content_list = await msg_details.to_list(page_size)

        page_res = dict(
            page_idx=page_idx,
            page_total_cnts=total_page,
            page_cap=page_size,
            page_data=msg_content_list
        )

        return get_std_json_response(data=jsontool.dumps(page_res, ensure_ascii=False))


class MyUtestShare(MyBaseHandler):
    @token_required()
    @deco_jsonp()
    async def get(self):
        """
        获取当前用户下的所有的utest分享链接
        :return:
        """
        return await get_org_data_paginator(self, col_name='share_test_report')


class MyProjectShare(MyBaseHandler):
    @token_required()
    @deco_jsonp()
    async def get(self):
        """
        获取当前用户下的所有的utest分享链接
        :return:
        """
        return await get_org_data_paginator(self, col_name='share_project_report')


class UpdateUtestShare(MyBaseHandler):
    @token_required()
    @deco_jsonp()
    async def post(self):
        """
        删除分享链接，直接完全删除，不需要留备份
        :return:
        """
        post_dict = self.get_post_body_dict()
        share_id = post_dict.get('share_id', None)
        mark = post_dict.get('mark', None)
        if list_have_none_mem(*[share_id, mark]):
            return ConstData.msg_args_wrong

        user = self.get_current_session_user()
        user_result = user.to_dict()
        res = await ShareTestReport.objects.get(id=ObjectId(str(share_id)), owner=user_result['id'])
        """:type:ShareTestReport"""
        if res is None:
            return ConstData.msg_forbidden
        res.mark = mark
        await res.save()
        return ConstData.msg_succeed


class DeleteUtestShare(MyBaseHandler):
    @token_required()
    @deco_jsonp()
    async def get(self):
        """
        删除分享链接，直接完全删除，不需要留备份
        :return:
        """
        share_id = self.get_argument('share_id', None)
        if list_have_none_mem(*[share_id]):
            return ConstData.msg_args_wrong
        user = self.get_current_session_user()
        user_result = user.to_dict()
        res = await ShareTestReport.objects.get(id=ObjectId(str(share_id)), owner=user_result['id'])
        """:type:ShareTestReport"""
        if res is None:
            return ConstData.msg_forbidden
        await res.complete_del()
        return ConstData.msg_succeed


class UpdateProjectShare(MyBaseHandler):
    @token_required()
    @deco_jsonp()
    async def post(self):
        """
        删除分享链接
        :return:
        """
        post_dict = self.get_post_body_dict()
        share_id = post_dict.get('share_id', None)
        mark = post_dict.get('mark', None)
        if list_have_none_mem(*[share_id, mark]):
            return ConstData.msg_args_wrong
        user = self.get_current_session_user()
        user_result = user.to_dict()
        res = await ShareProjectReport.objects.get(id=ObjectId(str(share_id)), owner=user_result['id'])
        """:type:ShareProjectReport"""
        if res is None:
            return ConstData.msg_forbidden
        res.mark = mark
        await res.save()
        return ConstData.msg_succeed


class DeleteProjectShare(MyBaseHandler):
    @token_required()
    @deco_jsonp()
    async def get(self):
        """
        删除分享链接
        :return:
        """
        share_id = self.get_argument('share_id', None)
        if list_have_none_mem(*[share_id]):
            return ConstData.msg_args_wrong
        user = self.get_current_session_user()
        user_result = user.to_dict()
        res = await ShareProjectReport.objects.get(id=ObjectId(str(share_id)), owner=user_result['id'])
        """:type:ShareProjectReport"""
        if res is None:
            return ConstData.msg_forbidden
        await res.complete_del()
        return ConstData.msg_succeed
