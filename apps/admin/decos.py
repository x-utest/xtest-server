# 和权限相关的装饰器
import functools
from dtlib.web.constcls import ConstData


def admin_required(is_async=True):
    def _async_token_required(method):
        @functools.wraps(method)
        async def wrapper(self, *args, **kwargs):
            """
            限制用户必须为超管
            :param self:
            :param args:
            :param kwargs:
            :return:
            """
            log_session = await self.set_session_by_token(cookie_enable=False)
            if log_session is None:
                self.write(ConstData.msg_unauthorized)
                return

            user = log_session['user']  # 获取当前用户
            db = self.get_async_mongo()
            user_col = db.g_users
            user_res = await user_col.find_one({'_id': user})
            if user_res is None or user_res['user_id'] != 'admin':
                self.write(ConstData.msg_forbidden)
                return

            if is_async:
                await method(self, *args, **kwargs)
            else:
                method(self, *args, **kwargs)

        return wrapper

    return _async_token_required
