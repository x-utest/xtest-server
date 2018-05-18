import math

from pymongo import DESCENDING
from dtlib.tornado.base_hanlder import MyUserBaseHandler
from bson import ObjectId
from dtlib import jsontool
from dtlib.randtool import generate_uuid_token
from dtlib.tornado.decos import token_required
from dtlib.utils import list_have_none_mem
from dtlib.web.constcls import ConstData
from dtlib.web.decos import deco_jsonp
from dtlib.web.tools import get_std_json_response

from dtlib.tornado.utils import get_org_data_paginator

from dtlib.tornado.utils import set_default_rc_tag

share_page = '/utest-report-share.html?stoken='  # 单独部署的一套前端内容

pro_share_page = '/pro-report-share.html?stoken='  # 单独部署的一套前端内容


class GetUtestShareLink(MyUserBaseHandler):
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

        db = self.get_async_mongo()
        share_col = db.share_test_report
        utest_col = db.unit_test_data
        proj_col = db.test_project

        # todo 做资源归属和权限的判断
        test_data = await utest_col.find_one({'_id': ObjectId(rep_id)})
        project = await proj_col.find_one({'_id': test_data['pro_id']})

        # if (project is None) or (project.organization is None):
        if project is None:
            return ConstData.msg_forbidden

        user_org = await self.get_organization()
        pro_org_id = project['organization']
        if pro_org_id != user_org:
            return ConstData.msg_forbidden

        share_obj = await share_col.find_one({'rep_id': rep_id})

        if share_obj is None:  # 如果不存在分享Link则创建一组
            stoken = generate_uuid_token()  # 生成一组随机串，分享的时候会看到

            share_data = dict(
                rep_id=rep_id,
                stoken=stoken,
                cnt=0,
                is_del=False,
                project=project['_id'],
                p_name=project['project_name'],
                owner=project['owner'],
                owner_name=project['owner_name'],
                organization=project['organization'],
                org_name=project['org_name']
            )
            # await share_obj.set_project_tag(project)
            # await share_obj.set_org_user_tag(http_req=self)
            share_data = set_default_rc_tag(share_data)
            await share_col.insert(share_data)
            share_url = share_page + stoken
        else:
            # 如果有，则直接使用
            share_url = share_page + share_obj['stoken']

        res_dict = dict(
            share_url=share_url
        )

        return get_std_json_response(data=jsontool.dumps(res_dict))


class GetUtestShareData(MyUserBaseHandler):
    """
    获取分享的单元测试数据接口
    """

    @deco_jsonp()
    async def get(self):
        stoken = self.get_argument('stoken', None)

        if list_have_none_mem(*[stoken]):
            return ConstData.msg_args_wrong

        db = self.get_async_mongo()
        share_col = db.share_test_report
        utest_col = db['unit_test_data']
        share_obj = await share_col.find_one({'stoken': stoken})

        if share_obj is None:
            return ConstData.msg_forbidden

        # todo 把完整的Unittest的报告内容获取出来并返回

        msg_details = utest_col.find({"_id": ObjectId(str(share_obj['rep_id']))})
        msg_content_list = await msg_details.to_list(1)

        msg_content = msg_content_list[0]

        # 做一个阅读访问次数的计数
        cnt = share_obj['cnt']
        if cnt is None:
            cnt = 0
        cnt += 1
        await share_col.update({'stoken': stoken}, {'$set':{'cnt': cnt}})

        return get_std_json_response(data=jsontool.dumps(msg_content, ensure_ascii=False))


class GetProjectShareLink(MyUserBaseHandler):
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
        tag = self.get_argument('tag', 'default')  # 测试报项目的ID

        if list_have_none_mem(*[pro_id]):
            return ConstData.msg_args_wrong

        # todo 做资源归属和权限的判断

        user_org = await self.get_organization()

        db = self.get_async_mongo()
        proj_col = db.test_project
        share_col = db.share_project_report

        project = await proj_col.find_one({'_id': ObjectId(str(pro_id))})

        if tag != 'default' and tag not in project['tags']:
            return ConstData.msg_args_wrong

        pro_org_id = project['organization']

        if (project is None) or (pro_org_id is None):
            return ConstData.msg_forbidden

        if pro_org_id != user_org:
            return ConstData.msg_forbidden

        #todo: delete default next release
        condition = {
            'pro_id': pro_id
        }
        if tag == 'default':
            condition['$or'] = [
                {'tag': 'default'},
                {'tag': {'$exists': False}}
            ]
        else:
            condition['tag'] = tag

        share_obj = await share_col.find_one(condition)

        if share_obj is None:  # 如果不存在分享Link则创建一组
            stoken = generate_uuid_token()  # 生成一组随机串，分享的时候会看到

            share_data = dict(
                pro_id=pro_id,
                stoken=stoken,
                cnt=0,
                project=project['_id'],
                p_name = project['project_name'],
                owner = project['owner'],
                owner_name = project['owner_name'],
                organization = project['organization'],
                org_name = project['org_name'],
                tag=tag
            )
            share_data = set_default_rc_tag(share_data)
            await share_col.insert(share_data)
            share_url = pro_share_page + stoken
        else:
            # 如果有，则直接使用
            share_url = pro_share_page + share_obj['stoken']

        res_dict = dict(
            share_url=share_url
        )

        return get_std_json_response(data=jsontool.dumps(res_dict))


class GetProjectShareData(MyUserBaseHandler):
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

        db = self.get_async_mongo()
        share_col = db.share_project_report
        utest_col = db['unit_test_data']

        share_obj = await share_col.find_one({'stoken': stoken})

        if share_obj is None:
            return ConstData.msg_forbidden

        # 做一个阅读访问次数的计数
        await share_col.update({'stoken': stoken}, {'$inc':{'cnt': 1}})

        condition = {
            "pro_id": share_obj['project'],
            "is_del": False
        }
        #todo: delete default next release
        if 'tag' in share_obj.keys():
            tag = share_obj['tag']
            if tag != 'default':
                condition['tag'] = tag
            else:
                condition['$or'] = [
                    {'tag': tag}, {'tag': {'$exists': False}}
                ]
        else:
            condition['$or'] = [
                {'tag': 'default'}, {'tag': {'$exists': False}}
            ]

        res = utest_col.find(
            condition, {"details": 0},
            sort=[('rc_time', DESCENDING)])

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


class MyUtestShare(MyUserBaseHandler):
    @token_required()
    @deco_jsonp()
    async def get(self):
        """
        获取当前用户下的所有的utest分享链接
        :return:
        """
        return await get_org_data_paginator(self, col_name='share_test_report')


class MyProjectShare(MyUserBaseHandler):
    @token_required()
    @deco_jsonp()
    async def get(self):
        """
        获取当前用户下的所有的utest分享链接
        :return:
        """
        return await get_org_data_paginator(self, col_name='share_project_report')


class UpdateUtestShare(MyUserBaseHandler):
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
        db = self.get_async_mongo()
        user_col = db.g_users
        share_col = db.share_test_report
        user_result = await user_col.find_one({'_id': ObjectId(user)})
        res = await share_col.find_one({'_id': ObjectId(str(share_id)), 'owner': user_result['_id']})

        if res is None:
            return ConstData.msg_forbidden

        await share_col.update({'_id': ObjectId(str(share_id)), 'owner': user_result['_id']},
                               {'$set': {'mark': mark}})
        return ConstData.msg_succeed


class DeleteUtestShare(MyUserBaseHandler):
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

        db = self.get_async_mongo()
        user_col = db.g_users
        share_col = db.share_test_report

        user_result = await user_col.find_one({'_id': ObjectId(user)})

        res = await share_col.find_one({'_id': ObjectId(str(share_id)), 'owner': user_result['_id']})
        """:type:ShareTestReport"""
        if res is None:
            return ConstData.msg_forbidden
        await share_col.remove({'_id': ObjectId(str(share_id)), 'owner': user_result['_id']})
        return ConstData.msg_succeed


class UpdateProjectShare(MyUserBaseHandler):
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
        db = self.get_async_mongo()
        user_col = db.g_users
        share_col = db.share_project_report
        user_result = await user_col.find_one({'_id': ObjectId(user)})
        res = await share_col.find_one({'_id': ObjectId(str(share_id)), 'owner': user_result['_id']})

        if res is None:
            return ConstData.msg_forbidden
        await share_col.update({'_id': ObjectId(str(share_id)), 'owner': user_result['_id']},
                               {'$set': {'mark': mark}})
        return ConstData.msg_succeed


class DeleteProjectShare(MyUserBaseHandler):
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

        db = self.get_async_mongo()
        share_proj_col = db.share_project_report

        res = await share_proj_col.find_one({'_id': ObjectId(str(share_id)), 'owner': ObjectId(user)})

        if res is None:
            return ConstData.msg_forbidden

        await share_proj_col.remove({'_id': ObjectId(str(share_id)), 'owner': ObjectId(user)})
        return ConstData.msg_succeed
