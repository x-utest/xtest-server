from xt_base.base_server import MyBaseHandler
from bson import ObjectId
from dtlib import jsontool
from dtlib.aio.decos import my_async_jsonp, my_async_paginator
from dtlib.tornado.decos import token_required
from dtlib.tornado.docs import TestDataApp
from dtlib.utils import list_have_none_mem
from dtlib.web.constcls import ConstData
from dtlib.web.tools import get_std_json_response

from xt_base.document.base_docs import Project
from xt_base.utils import get_org_data
from xt_base.utils import get_org_data_paginator


class ListProjectsNote(MyBaseHandler):
    """
    根据当前组织得到appid，key
    """

    @token_required()
    @my_async_jsonp
    async def get(self):
        project_id = self.get_argument('project_id', None)
        if project_id is None:
            return ConstData.msg_args_wrong
        project_obj = await Project.objects.get(id=ObjectId(str(project_id)))
        organization = project_obj.organization
        test_data_app = await TestDataApp.objects.get(organization=organization)
        data = dict()
        data['project_name'] = project_obj.project_name
        data['project_id'] = project_obj._id
        data['app_id'] = test_data_app.app_id
        data['app_key'] = test_data_app.app_key
        res_str = get_std_json_response(code=200, data=jsontool.dumps(data))

        return res_str


class CreateTestProject(MyBaseHandler):
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

        project_obj = Project()
        project_obj.project_name = project_name
        project_obj.mark = mark
        project_obj.organization = organization
        project_obj.org_name = organization.name
        project_obj.owner = user
        project_obj.owner_name = user.nickname
        project_obj.set_default_rc_tag()

        result = await project_obj.save()

        res_str = get_std_json_response(code=200, data=jsontool.dumps(result.to_dict()))

        return res_str


class UpdateTestProject(MyBaseHandler):
    """
    更新project的name
    """

    @token_required()
    @my_async_jsonp
    async def post(self):
        post_json = self.get_post_body_dict()

        id = post_json.get('id', None)
        project_name = post_json.get('name', None)
        mark = post_json.get('mark', None)

        if list_have_none_mem(*[id, project_name, mark]):
            return ConstData.msg_args_wrong

        # todo 做资源归属和权限的判断
        project_obj = await Project.objects.get(id=ObjectId(str(id)))
        user_org = await self.get_organization()

        if (project_obj is None) or (project_obj.organization is None):
            return ConstData.msg_forbidden

        pro_org_id = project_obj.organization.get_id()
        if pro_org_id != user_org.get_id():
            return ConstData.msg_forbidden

        project_obj.project_name = project_name
        project_obj.mark = mark

        result = await project_obj.save()

        res_str = get_std_json_response(code=200, data=jsontool.dumps(result.to_dict()))

        return res_str


class DeleteTestProject(MyBaseHandler):
    """
    删除project（实际是将is_del设置为true）
    """

    @token_required()
    @my_async_jsonp
    async def get(self):
        id = self.get_argument('id', None)
        if id is None:
            return ConstData.msg_args_wrong

        # todo 做资源归属和权限的判断
        project_obj = await Project.objects.get(id=ObjectId(str(id)))
        user_org = await self.get_organization()

        if (project_obj is None) or (project_obj.organization is None):
            return ConstData.msg_forbidden

        pro_org_id = project_obj.organization.get_id()
        if pro_org_id != user_org.get_id():
            return ConstData.msg_forbidden

        project_obj.is_del = True
        result = await project_obj.save()
        return ConstData.msg_succeed


class ReadProjectsRecord(MyBaseHandler):
    """
    根据project—id查找30次的构建情况
    """

    @token_required()
    @my_async_jsonp
    async def get(self):
        id = self.get_argument('id', None)
        if id is None:
            return ConstData.msg_args_wrong

        # todo 做资源归属和权限的判断
        project_obj = await Project.objects.get(id=ObjectId(str(id)))
        user_org = await self.get_organization()

        if (project_obj is None) or (project_obj.organization is None):
            return ConstData.msg_forbidden

        pro_org_id = project_obj.organization.get_id()
        if pro_org_id != user_org.get_id():
            return ConstData.msg_forbidden

        return await get_org_data_paginator(self, col_name='unit_test_data', pro_id=id, hide_fields={'details': 0})


class ListProjects(MyBaseHandler):
    """
    本组织的所有的项目列出来
    """

    @token_required()
    @my_async_jsonp
    @my_async_paginator
    async def get(self):
        return await get_org_data(self, cls_name=Project)
