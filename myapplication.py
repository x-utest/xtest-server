from tornado.web import Application

from dtlib.tornado.const_data import FieldDict
from dtlib.web.valuedict import ValueDict

commentKeep_ValueDict = ValueDict(0, '')


class MyApplication(Application):
    """
    加入一些自定义的应用
    """

    def set_async_redis(self, async_rc_pool):
        """
        设置连接池
        :param async_rc_pool:
        :return:
        """
        self.settings[FieldDict.key_async_redis_pool] = async_rc_pool
        pass

    def set_sync_redis(self, sync_rc_pool):
        """
        获取同步类型的redis的连接池
        :return:
        """
        self.settings[FieldDict.key_sync_redis_pool] = sync_rc_pool
        pass

    def set_async_mongo(self, async_mongo_pool):
        """
        异步的mongo连接池
        :param async_mongo_pool:
        :return:
        """
        self.settings[FieldDict.key_async_mongo_pool] = async_mongo_pool
