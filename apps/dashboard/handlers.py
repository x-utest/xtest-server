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
from xt_base.base_server import MyBaseHandler


class UpdateContent(MyBaseHandler):
    """
    更新文本内容
    """

    def __init__(self, *args, **kwargs):
        super(UpdateContent, self).__init__(*args, **kwargs)

    @token_required()
    @deco_jsonp()
    async def post(self, *args, **kwargs):
        content_id = self.get_argument('content_id', None)
        pro_id = self.get_argument('pro_id', "5a7fb0cd47de9d5cf3d13a44")
        group = self.get_argument('group', "test")
        time_stamp = self.get_argument('date_time', None)
        content = self.get_argument('content', None)
        if list_have_none_mem(*[pro_id, group, time_stamp, content]):
            return ConstData.msg_args_wrong
        mongo_coon = self.get_async_mongo()
        mycol = mongo_coon['dashboard_content']
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
            _id = await mycol.insert(data)
            msg_succeed = '{"code":%s,"msg":"%s","data":{"_id": "%s"}}' % (ResCode.ok, "success", _id)
            return msg_succeed


class DeleteContent(MyBaseHandler):
    """
    删除文本内容
    """

    def __init__(self, *args, **kwargs):
        super(DeleteContent, self).__init__(*args, **kwargs)

    @token_required()
    @deco_jsonp()
    async def post(self, *args, **kwargs):
        content_id = self.get_argument('content_id', None)
        # pro_id = self.get_argument('pro_id', "5a7fb0cd47de9d5cf3d13a44")
        if list_have_none_mem(*[content_id]):
            return ConstData.msg_args_wrong
        mongo_coon = self.get_async_mongo()
        mycol = mongo_coon['dashboard_content']
        mycol.update({'_id': ObjectId(content_id)}, {'$set': {'is_del': True}}, upsert=False)
        return ConstData.msg_succeed


class GetContent(MyBaseHandler):
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
        mongo_coon = self.get_async_mongo()
        mycol = mongo_coon[col_name]

        if pro_id is None:
            msg_details = mycol.find({
                "is_del": False
            }, hide_fields).sort([('date_time', DESCENDING)])  # 升序排列
        else:
            msg_details = mycol.find({
                'pro_id': ObjectId(pro_id),
                "is_del": False
            }, hide_fields).sort([('date_time', DESCENDING)])  # 升序排列

        msg_details_cnt = await msg_details.count()
        page_size = page_cap if page_cap < msg_details_cnt else msg_details_cnt
        msg_content_list = await msg_details.to_list(page_size)
        return get_std_json_response(data=jsontool.dumps(msg_content_list))


class UpdateProjectShow(MyBaseHandler):
    """
    更新项目是否展示的状态
    """

    def __init__(self, *args, **kwargs):
        super(UpdateProjectShow, self).__init__(*args, **kwargs)

    @deco_jsonp()
    async def post(self, *args, **kwargs):
        tv = self.get_argument('tv', None)
        pro_id = self.get_argument('pro_id', None)
        if list_have_none_mem(*[tv, pro_id]):
            return ConstData.msg_args_wrong
        if tv not in ['true', 'false']:
            return ConstData.msg_args_wrong
        tv = True if tv == 'true' else False
        mongo_coon = self.get_async_mongo()
        mycol = mongo_coon['test_project']
        mycol.update({'_id': ObjectId(pro_id)}, {'$set': {'tv': tv}}, upsert=False)
        return ConstData.msg_succeed

# code trash

# class getDevRSS(MyBaseHandler):
#     """
#     处理开发 RSS 消息
#     """
#
#     def __init__(self, *args, **kwargs):
#         super(getDevRSS, self).__init__(*args, **kwargs)
#         self.set_header('Access-Control-Allow-Origin', '*')
#         self.set_header('Access-Control-Allow-Headers',
#                         'Origin, X-Requested-With, Content-type, Accept, connection, User-Agent, Cookie')
#         self.set_header('Access-Control-Allow-Methods',
#                         'POST, GET, OPTIONS')
#
#     async def get(self):
#         rss_file = 'bbRSS'
#         with open(rss_file, 'r+') as f:
#             content = f.read()
#             self.finish(content)
#             filemt = time.localtime(os.stat(rss_file).st_mtime)
#             filemt = time.mktime(filemt)
#             nowtime = time.mktime(time.localtime())
#             if nowtime - filemt < 60:
#                 return
#             res = await self.get_new_rss_content()
#             f.seek(0)
#             f.truncate()
#             f.write(res)
#
#     async def get_new_rss_content(self):
#         url = "https://bitbucket.org/gt-dev/gt-server/rss?token=46199f51a3313408e63f7318bdb20b48"
#         res = requests.get(url).text
#         return res
#
#
# class ServerSentEvent(MyBaseHandler):
#
#     def __init__(self, *args, **kwargs):
#         super(ServerSentEvent, self).__init__(*args, **kwargs)
#         self.set_header('Access-Control-Allow-Origin', '*')
#         self.set_header('Access-Control-Allow-Headers',
#                         'Origin, X-Requested-With, Content-type, Accept, connection, User-Agent, Cookie')
#         self.set_header('Access-Control-Allow-Methods',
#                         'POST, GET, OPTIONS')
#         self.set_header('Content-Type', 'text/event-stream')
#
#     @token_required()
#     async def get(self):
#         # pro_id = self.get_argument('id', None)
#         pro_id = self.get_argument('id', "5a7fb0cd47de9d5cf3d13a44")
#         mongo_coon = self.get_async_mongo()
#         mycol = mongo_coon['unit_test_data']
#         res = await mycol.find_one(
#             {
#                 "pro_id": ObjectId(str(pro_id)),
#                 "is_del": False
#             }, {"rc_time": 1},
#             sort=[('rc_time', DESCENDING)])
#         latest_test_time = res['rc_time']
#         while True:
#             res = await mycol.find_one(
#             {
#                 "pro_id": ObjectId(str(pro_id)),
#                 "is_del": False
#             }, {"rc_time": 1},
#             sort=[('rc_time', DESCENDING)])
#             if res['rc_time'] > latest_test_time:
#                 latest_test_time = res['rc_time']
#                 self.write('data:0\n\n')
#                 self.flush()
#             time.sleep(2)
#             self.write('data: 1\n\n')
#             self.flush()


# class UpdateVersionInfo(MyBaseHandler):
#     """
#     存取项目的具体信息
#     """
#
#     def __init__(self, *args, **kwargs):
#         super(UpdateVersionInfo, self).__init__(*args, **kwargs)
#         self.set_header('Access-Control-Allow-Origin', '*')
#         self.set_header('Access-Control-Allow-Headers',
#                         'Origin, X-Requested-With, Content-type, Accept, connection, User-Agent, Cookie')
#         self.set_header('Access-Control-Allow-Methods',
#                         'POST, GET, OPTIONS')
#
#     async def post(self, *args, **kwargs):
#         project_id = self.get_argument('pro_id', None)
#         version = self.get_argument('version', None)
#         test_server = self.get_argument('server', None)
#         requirement = self.get_argument('requirement', None)
#         # TODO: last_test id get from test data
#         res_dict = dict(
#             project_id=project_id,
#             version=version,
#             test_server=test_server,
#             requirement=requirement,
#         )
#         # print(res_dict)
#         self.write(res_dict)
#
#
# class GetVersionInfo(MyBaseHandler):
#     """
#     存取项目的具体信息
#     """
#
#     def __init__(self, *args, **kwargs):
#         super(GetVersionInfo, self).__init__(*args, **kwargs)
#         self.set_header('Access-Control-Allow-Origin', '*')
#         self.set_header('Access-Control-Allow-Headers',
#                         'Origin, X-Requested-With, Content-type, Accept, connection, User-Agent, Cookie')
#         self.set_header('Access-Control-Allow-Methods',
#                         'POST, GET, OPTIONS')
#
#     async def get(self, *args, **kwargs):
#         # version = self.get_argument('version')
#         """
#         status: -1: None
#                 0: in progress
#                 1: success
#                 2: fail
#         :param args:
#         :param kwargs:
#         :return:
#         """
#         version="18.04.08.01"
#         pro_id="5a7fb0cd47de9d5cf3d13a44"
#         test_content = await self.get_test_data(pro_id, version)
#         test_design = {
#             # todo: get content from mongo
#             'requirement': {
#                 'content': "这是项目需求\n\n第一条: xxxxxxxxx\n第一条: xxxxxxxxx\n第一条: xxxxxxxxx\n第一条: xxxxxxxxx",
#                 'status': 0
#             },
#             # todo: get content from rss
#             'dev_rss': {
#                 'content': "这是RSS\n\n第一条: xxxxxxxxx\n第一条: xxxxxxxxx\n第一条: xxxxxxxxx\n第一条: xxxxxxxxx",
#                 'status': 0
#             },
#             # todo: get content from mongo
#             'test': {
#                 'content': "这是用例分析\n\n第一条: xxxxxxxxx\n第一条: xxxxxxxxx\n第一条: xxxxxxxxx\n第一条: xxxxxxxxx",
#                 'status': 0
#             },
#         }
#         if test_content:
#             print(test_content)
#             status = 1 if test_content["was_successful"] is True else 2
#         else:
#             test_design_status = reduce(lambda x, y: x+y, [v['status'] for v in test_design.values()])
#             status = -1 if test_design_status < 3 else 0
#         api_test = {
#             'status': status,
#             'content': test_content
#         }
#         # step = {"needs": 4, 'have_done': 0}
#         info = dict(
#             test_design=test_design,
#             api_test=api_test,
#             version=version,
#             # step=step
#             pro_id=pro_id,
#         )
#         self.write(info)
#
#     async def get_test_data(self, pro_id, version):
#         mongo_coon = self.get_async_mongo()
#         mycol = mongo_coon['unit_test_data']
#
#         # user_org = await self.get_organization()
#         """:type:Organization"""
#
#         msg_details = mycol.find({
#             # "organization": user_org.get_id(),
#             "pro_version": version,
#             "pro_id": ObjectId(pro_id),
#             "is_del": False,
#             # "_id": ObjectId(str("5ac9e8e847de9d0c16cb927f"))
#         }).sort([('rc_time', DESCENDING)])  # 升序排列
#
#         msg_content_list = await msg_details.to_list(1)
#
#         print(msg_content_list)
#
#         try:
#             msg_content = msg_content_list[0]
#
#             return get_std_json_response(data=jsontool.dumps(msg_content, ensure_ascii=False))
#         except:
#             return None
#
