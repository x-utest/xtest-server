#  coding:utf-8
"""

- 可以使用tornado server
- 修改ioloop绑定后,可多核启动

"""

import asyncio
import logging

import motor.motor_asyncio
from tabulate import tabulate

import config
from config import HTTP_PORT, settings, mongodb_cfg, LOGGING_LEVEL, debug_mode, SERVER_PROCESS
from dtlib.dtlog import dlog
from dtlib.tornado.async_server import MyAsyncHttpServer
from route import urls
from myapplication import MyApplication


def output_server_info():
    """
    输出服务器相关配置信息
    :param kwargs:
    :return:
    """

    tbl_out = tabulate([
        ['app_version', config.app_version],
        ['http_port', config.HTTP_PORT],
        ['process_num ', config.SERVER_PROCESS],
        ['db_server', config.mongodb_cfg.host]
    ],
        tablefmt='grid')
    print(tbl_out)
    print('http://127.0.0.1:%s' % config.HTTP_PORT)


async def auth_mongodb(**kwargs):
    """
    异步身份认证mongodb
    :type future:asyncio.Future
    :param kwargs:
    :return:
    """
    mongo_conn = kwargs.get('mongo_conn', None)

    if mongo_conn is None:
        raise ValueError

    res = await mongo_conn.authenticate(
        mongodb_cfg.user_name,
        mongodb_cfg.user_pwd,
    )
    if res is True:
        print('mongodb authenticate succeed...')

async def auth_mongo(**kwargs):

    db = kwargs.get('db', None)

    if mongo_conn is None:
        raise ValueError
    res = await db.authenticate(
        mongodb_cfg.user_name,
        mongodb_cfg.user_pwd,
    )

    if res is True:
        print('mongodb authenticate succeed...')

if __name__ == '__main__':
    # 设置日志输出级别
    dlog.setLevel(LOGGING_LEVEL)
    logging.getLogger('asyncio').setLevel(logging.WARNING)

    # 输出运行服务的相关信息
    output_server_info()

    app = MyApplication(
        urls,
        **settings
    )

    server = MyAsyncHttpServer(
        app,
        xheaders=True  # when running behind a load balancer like nginx
    )
    server.bind(HTTP_PORT)  # 设置端口
    server.start(num_processes=SERVER_PROCESS)  # if 0,forks one process per cpu,#TORNADO_SERVER_PROCESS

    # asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())  # 使用uvloop来进行loop替换
    io_loop = asyncio.get_event_loop()
    io_loop.set_debug(debug_mode)

    # 设置Mongodb
    # you only need to keep track of the DB instance if you connect to multiple databases.
    mongo_conn = motor.motor_asyncio.AsyncIOMotorClient(mongodb_cfg.host,mongodb_cfg.port)
    # mongo_conn.max_pool_size = mongodb_cfg.max_connections  # mongodb连接池最大连接数
    db=mongo_conn.xtest
    io_loop.run_until_complete(auth_mongo(db=db))  # 数据库认证

    # 设置异步mongo连接，方便后续直接非ORM操作，比如请求大量的数据
    app.set_async_mongo(db)

    io_loop.run_forever()
