import dtlib
from dtlib import jsontool
from dtlib import timetool
from dtlib.mongo.utils import get_mongodb_version, get_pip_list, get_python_version
from dtlib.tornado.decos import test_token_required, api_counts
from dtlib.web.decos import deco_jsonp
from dtlib.web.tools import get_std_json_response
from tornado.web import RequestHandler

from config import app_version, test_token
from xt_base.base_server import MyBaseHandler


class MainHandler(RequestHandler):
    """
    本接口的首页信息
    """

    def get(self):
        self.write('This the Home Page')


class AppInfo(MyBaseHandler):
    """
    获取本web应用的基本信息
    """

    # @api_counts()
    @deco_jsonp(is_async=False)
    def get(self):
        print('run app-info:', app_version)
        res = dict(
            server='tornado',  # web服务器
            app_version=app_version,  # 应用版本
            dtlib_version=dtlib.VERSION,  # 第三方库dt-lib的版本
            req_time=timetool.get_current_time_string(),  # 当前查询时间点
            timezone=timetool.get_time_zone(),  # 当前服务器的时区
        )
        return get_std_json_response(data=jsontool.dumps(res, ensure_ascii=False))


class PrivateAppInfo(MyBaseHandler):
    """
    获取本web应用的基本信息,这些需要有管理员的test_key才能访问
    """

    @test_token_required(test_token=test_token)
    @deco_jsonp(is_async=False)
    def get(self):
        print('run app-info:', app_version)

        mongo_version = get_mongodb_version()
        pip_list = get_pip_list()
        python = get_python_version()

        res = dict(
            server='tornado',  # web服务器
            app_version=app_version,  # 应用版本
            dtlib_version=dtlib.VERSION,  # 第三方库dt-lib的版本
            req_time=timetool.get_current_time_string(),  # 当前查询时间点
            timezone=timetool.get_time_zone(),  # 当前服务器的时区

            mongo_server=mongo_version,  # mongo的服务器版本号
            python=python,  # python版本号
            pip_list=pip_list,  # 安装的pip_list
        )
        return get_std_json_response(data=jsontool.dumps(res, ensure_ascii=False))


class GetClientInfo(MyBaseHandler):
    @deco_jsonp(is_async=False)
    def get(self):
        """
        返回客户端的公网IP地址及端口
        :return: 
        """

        client_req = self.request

        res_dict = dict(
            remote_ip=client_req.remote_ip,
            method=client_req.method,
            path=client_req.path,
            headers=client_req.headers._dict

        )

        return get_std_json_response(data=jsontool.dumps(res_dict))


class CreateServerAsset(MyBaseHandler):
    """
    创建服务器资产
    """

    async def post(self):
        return 'hello'
