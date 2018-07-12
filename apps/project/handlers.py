from dtlib.tornado.base_hanlder import MyUserBaseHandler
from bson import ObjectId
from dtlib import jsontool
from dtlib.aio.decos import my_async_jsonp, my_async_paginator
from dtlib.tornado.decos import token_required
from dtlib.utils import list_have_none_mem
from dtlib.web.constcls import ConstData, ResCode
from dtlib.web.tools import get_std_json_response

from dtlib.tornado.utils import get_org_data
from dtlib.tornado.utils import get_org_data_paginator

from dtlib.web.decos import deco_jsonp
from dtlib.tornado.utils import set_default_rc_tag
from apps.admin.decos import admin_required


class ListProjectsNote(MyUserBaseHandler):
    """
    根据当前组织得到appid，key
    """

    @token_required()
    @my_async_jsonp
    async def get(self):
        project_id = self.get_argument('project_id', None)
        if project_id is None:
            return ConstData.msg_args_wrong
        db = self.get_async_mongo()
        proj_col = db.test_project
        project_obj = await proj_col.find_one({'_id': ObjectId(str(project_id))})
        organization = project_obj['organization']
        app_col = db.test_data_app
        test_data_app = await app_col.find_one({'organization': organization})
        data = dict(
            project_name=project_obj['project_name'],
            project_id=project_obj['_id'],
            app_id=test_data_app['app_id'],
            app_key=test_data_app['app_key']
        )
        res_str = get_std_json_response(code=200, data=jsontool.dumps(data))

        return res_str


class CreateTestProject(MyUserBaseHandler):
    """
    项目名称
    """

    @token_required()
    @my_async_jsonp
    async def post(self):
        post_json = self.get_post_body_dict()

        mark = post_json.get('mark', None)
        project_name = post_json.get('name', None)

        organization = await self.get_organization()
        user = self.get_current_session_user()

        db = self.get_async_mongo()
        proj_col = db.test_project
        org_col = db.organization
        org_res = await org_col.find_one({'_id': ObjectId(organization)})
        org_name = org_res['name']
        user_col = db.g_users
        user_res = await user_col.find_one({'_id': ObjectId(user)})
        user_nickname = user_res['nickname']
        new_data = dict(
            project_name=project_name,
            mark=mark,
            organization=organization,
            org_name=org_name,
            owner=user,
            owner_name=user_nickname,
        )
        new_data = set_default_rc_tag(new_data)

        result = await proj_col.insert_one(new_data)

        res_str = get_std_json_response(code=200, data=jsontool.dumps(result.inserted_id))

        return res_str


class UpdateTestProject(MyUserBaseHandler):
    """
    更新project的name
    """

    @admin_required()
    @my_async_jsonp
    async def post(self):
        post_json = self.get_post_body_dict()

        id = post_json.get('id', None)
        project_name = post_json.get('name', None)
        mark = post_json.get('mark', None)

        if list_have_none_mem(*[id, project_name, mark]):
            return ConstData.msg_args_wrong

        # todo 做资源归属和权限的判断
        db = self.get_async_mongo()
        proj_col = db.test_project
        project_obj = await proj_col.find_one({'_id': ObjectId(str(id))})
        user_org = await self.get_organization()

        organization = project_obj['organization']
        if (project_obj is None) or (organization is None):
            return ConstData.msg_forbidden

        pro_org_id = organization
        if pro_org_id != user_org:
            return ConstData.msg_forbidden

        data = dict(
            project_name=project_name,
            mark=mark
        )
        result = await proj_col.update({'_id': ObjectId(str(id))}, {'$set': data}, upsert=False)
        res_str = get_std_json_response(code=200, data=jsontool.dumps(result))

        return res_str


class DeleteTestProject(MyUserBaseHandler):
    """
    删除project（实际是将is_del设置为true）
    """

    @admin_required()
    @my_async_jsonp
    async def get(self):
        id = self.get_argument('id', None)
        if id is None:
            return ConstData.msg_args_wrong

        # todo 做资源归属和权限的判断
        db = self.get_async_mongo()
        proj_col = db.test_project
        test_data_col = db.unit_test_data
        project_obj = await proj_col.find_one({'_id': ObjectId(str(id))})
        user_org = await self.get_organization()

        if project_obj is None:
            return ConstData.msg_forbidden

        pro_org_id = project_obj['organization']
        if pro_org_id != user_org:
            return ConstData.msg_forbidden

        await proj_col.update({'_id': ObjectId(str(id))}, {'$set': {'is_del': True}}, upsert=False)
        # 删除附属于项目的测试结果
        await test_data_col.update({'pro_id': ObjectId(str(id))}, {'$set': {'is_del': True}}, multi=True)
        return ConstData.msg_succeed


class ReadProjectsRecord(MyUserBaseHandler):
    """
    根据project—id查找30次的构建情况
    """

    @token_required()
    @my_async_jsonp
    async def get(self):
        id = self.get_argument('id', None)
        tag = self.get_argument('tag')
        if id is None:
            return ConstData.msg_args_wrong

        # todo 做资源归属和权限的判断
        db = self.get_async_mongo()
        proj_col = db.test_project
        project_obj = await proj_col.find_one({'_id': ObjectId(id)})
        user_org = await self.get_organization()

        if project_obj is None:
            return ConstData.msg_forbidden

        pro_org_id = project_obj['organization']
        if pro_org_id != user_org:
            return ConstData.msg_forbidden

        return await get_org_data_paginator(self, col_name='unit_test_data', pro_id=id, tag=[tag],
                                            hide_fields={'details': 0})


class ListProjects(MyUserBaseHandler):
    """
    本组织的所有的项目列出来
    """

    @token_required()
    @my_async_jsonp
    @my_async_paginator
    async def get(self):
        return await get_org_data(self, collection='test_project')


class GetProjectTags(MyUserBaseHandler):
    """
    获取某个项目的所有tag
    """

    # @my_async_jsonp
    @my_async_jsonp
    async def get(self):
        pro_id = self.get_argument('pro_id', None)
        if pro_id is None:
            return ConstData.msg_args_wrong
        db = self.get_async_mongo()
        pro_col = db.test_project
        tags = await pro_col.find_one({'_id': ObjectId(pro_id)}, {'tags': 1})
        # test_data_col = db.unit_test_data
        # tags = await test_data_col.distinct("tag",
        #                                     {"pro_id": ObjectId(pro_id), 'is_del': False, 'tag': {'$exists': True}})
        tag_list = list()
        if 'tags' in tags.keys():
            tag_list = tags['tags']
        msg_succeed = '{"code":%s,"msg":"success","data":%s}' % (ResCode.ok, jsontool.dumps(tag_list))  # 操作成功
        return msg_succeed
