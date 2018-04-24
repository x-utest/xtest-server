"""
初始化app的运行环境
- 多核心环境设计有竞争的资源时,会有线程冲突
"""
import asyncio
import motor

from config import mongodb_cfg
from dtlib.mongo.utils import set_mongo_ttl_index


async def init_mongo():
    """
    不能在多核心状态进行设置
    :return:
    """
    mongo_conn = motor.MotorClient(
        host=mongodb_cfg.host,
        port=mongodb_cfg.port,
    )
    db = mongo_conn[mongodb_cfg.db_name]

    res = await db.authenticate(
        mongodb_cfg.user_name,
        mongodb_cfg.user_pwd,
    )
    if res is True:
        log_session = mongo_conn.log_session
        index_filed_name = 'last_use_time'
        ttl_seconds = 60 * 60 * 48  # 2days
        await set_mongo_ttl_index(log_session, index_filed_name, ttl_seconds)
        print('set session ttl succeed...')


if __name__ == '__main__':
    init_loop = asyncio.get_event_loop()
    init_loop.run_until_complete(init_mongo())
    # init_loop.stop()
    print('init app succeed')
