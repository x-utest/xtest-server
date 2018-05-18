import functools

from dtlib.tornado.decos import api_counts
from dtlib.web.constcls import ConstData
from dtlib.web.tools import get_jsonp_res

# from xt_base.document.auth2_docs import AuthAccessToken


def async_auth_access_token_required(method):
    """
    - 认证平台的access_token
    :param method:
    :return:
    """

    @api_counts()
    @functools.wraps(method)
    async def wrapper(self, *args, **kwargs):
        """
        :type self MyUserBaseHandler
        """
        callback = self.get_argument('callback', None)
        token = self.get_argument('token', None)

        self.set_header('Content-Type', 'application/json')
        self.set_header('charset', 'utf-8')

        if token is None:
            self.write(get_jsonp_res(callback, ConstData.msg_unauthorized))
            return

        self.set_cookie('token', token)

        log_session = await AuthAccessToken.objects.get(token=token)
        """:type:AuthAccessToken"""

        if log_session is None:
            self.write(get_jsonp_res(callback, ConstData.msg_unauthorized))
            return

        # 在此处直接赋值存储session,一些临时变量在此处缓存
        self.token = token  # 本次请求都会用到token,相当于会话标识
        self.cache_log_session = log_session

        await method(self, *args, **kwargs)

    return wrapper
