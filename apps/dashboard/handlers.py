# from dtlib.web.tools import get_std_json_response
# from dtlib import jsontool
# from bson import ObjectId
# from pymongo import DESCENDING
# from functools import reduce
import time
from pymongo import DESCENDING
from bson import ObjectId
from dtlib import jsontool
from dtlib.web.decos import deco_jsonp
from dtlib.web.constcls import ConstData, ResCode
from dtlib.web.tools import get_std_json_response
from dtlib.utils import list_have_none_mem
from dtlib.aio.base_mongo import wrap_default_rc_tag
from dtlib.tornado.decos import token_required
from dtlib.tornado.base_hanlder import MyUserBaseHandler

import json


class UpdateContent(MyUserBaseHandler):
    """
    更新文本内容
    """

    def __init__(self, *args, **kwargs):
        super(UpdateContent, self).__init__(*args, **kwargs)

    @token_required()
    @deco_jsonp()
    async def post(self, *args, **kwargs):
        post_json = self.get_post_body_dict()
        content_id = post_json.get('content_id', None)
        pro_id = post_json.get('pro_id', "5a7fb0cd47de9d5cf3d13a44")
        group = post_json.get('group', "test")
        time_stamp = post_json.get('date_time', None)
        content = post_json.get('content', None)

        if list_have_none_mem(*[pro_id, group, time_stamp, content]):
            return ConstData.msg_args_wrong
        mongo_conn = self.get_async_mongo()
        mycol = mongo_conn['dashboard_content']
        timeArray = time.localtime(int(time_stamp) / 1000.0)
        date_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        data = dict(
            pro_id=ObjectId(pro_id),
            group=group,
            date_time=date_time,
            content=content,
        )
        data = wrap_default_rc_tag(data)  # 加上默认的标签
        if content_id:
            await mycol.update({'_id': ObjectId(content_id)}, {'$set': data}, upsert=True)
            return ConstData.msg_succeed
        else:
            _id = await mycol.insert_one(data)
            msg_succeed = '{"code":%s,"msg":"%s","data":{"_id": "%s"}}' % (ResCode.ok, "success", _id)
            return msg_succeed


class DeleteContent(MyUserBaseHandler):
    """
    删除文本内容
    """

    def __init__(self, *args, **kwargs):
        super(DeleteContent, self).__init__(*args, **kwargs)

    @token_required()
    @deco_jsonp()
    async def post(self, *args, **kwargs):
        post_json = self.get_post_body_dict()
        content_id = post_json.get('content_id', None)
        # pro_id = self.get_argument('pro_id', "5a7fb0cd47de9d5cf3d13a44")
        if list_have_none_mem(*[content_id]):
            return ConstData.msg_args_wrong
        mongo_conn = self.get_async_mongo()
        mycol = mongo_conn['dashboard_content']
        mycol.update({'_id': ObjectId(content_id)}, {'$set': {'is_del': True}}, upsert=False)
        return ConstData.msg_succeed


class GetContent(MyUserBaseHandler):
    def __init__(self, *args, **kwargs):
        super(GetContent, self).__init__(*args, **kwargs)

    @token_required()
    @deco_jsonp()
    async def get(self, *args, **kwargs):
        hide_fields = {
            'rc_time': 0,
            'del_time': 0,
            'is_del': 0,
            'pro_id': 0
        }
        return await self.get_content_list(col_name='dashboard_content', hide_fields=hide_fields)

    async def get_content_list(self, *args, **kwargs):
        """
        直接传入项目名称和表的名称,返回分页的信息
        :param self:
        :param args:
        :param kwargs:col_name
        :return:
        """
        page_cap = self.get_argument('page_cap', '10')  # 一页的记录容量-var
        pro_id = self.get_argument('pro_id', None)

        col_name = kwargs.get('col_name', None)
        hide_fields = kwargs.get('hide_fields', None)  # 需要隐藏的字段,一个dict
        """:type:dict"""

        if list_have_none_mem(*[col_name, pro_id, page_cap]):
            return ConstData.msg_args_wrong
        page_cap = int(page_cap)
        mongo_conn = self.get_async_mongo()
        mycol = mongo_conn[col_name]

        if pro_id is None:
            msg_details = mycol.find({
                "is_del": False
            }, hide_fields).sort([('date_time', DESCENDING)])  # 升序排列
        else:
            msg_details = mycol.find({
                'pro_id': ObjectId(pro_id),
                "is_del": False
            }, hide_fields).sort([('date_time', DESCENDING)])  # 升序排列

        msg_details_cnt = await msg_details.count_documents()
        page_size = page_cap if page_cap < msg_details_cnt else msg_details_cnt
        msg_content_list = await msg_details.to_list(page_size)
        return get_std_json_response(data=jsontool.dumps(msg_content_list))


class UpdateProjectShow(MyUserBaseHandler):
    """
    更新项目是否展示的状态
    """

    def __init__(self, *args, **kwargs):
        super(UpdateProjectShow, self).__init__(*args, **kwargs)

    @deco_jsonp()
    async def post(self, *args, **kwargs):
        post_json = self.get_post_body_dict()
        tv_tags = post_json.get('tv_tags', None)
        pro_id = post_json.get('pro_id', None)

        if list_have_none_mem(*[tv_tags, pro_id]):
            return ConstData.msg_args_wrong
        if not isinstance(tv_tags, list):
            return ConstData.msg_args_wrong
        mongo_conn = self.get_async_mongo()
        mycol = mongo_conn['test_project']
        project = await mycol.find_one({'_id': ObjectId(pro_id)}, {'tags': 1})
        if 'tags' in project:
            tags = project['tags']
            if set(tv_tags).issubset(set(tags)) is False:
                return ConstData.msg_args_wrong
        await mycol.update({'_id': ObjectId(pro_id)}, {'$set': {'tv_tags': tv_tags}}, upsert=False)
        return ConstData.msg_succeed
