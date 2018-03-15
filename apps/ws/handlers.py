# coding:utf-8

"""
建立长连接的websocket
"""
from tornado import websocket
from tornado.gen import coroutine
from dtlib.tornado.tools import call_subprocess
from config import AUTOTEST_CMD


class ApiTestsSocket(websocket.WebSocketHandler):
    """
    执行API脚本的WS请求
    """

    ws_client = None  # 请求的客户端

    def check_origin(self, origin):
        return True

    def open(self):
        """
        连接websocket服务器时进行的event
        """

        ApiTestsSocket.ws_client = self  # 添加websocket

        print("WebSocket opened")

    @coroutine
    def on_message(self, message):
        """
        收到信息的时候进行的动作
        """
        # write_message用于主动写信息，这里将收到的信息原样返回
        # yield sleep(5)
        print('Websocket receive message')
        # self.write_message(ConstData.msg_fail)
        if message == "exec_api_tests":
            cmd = AUTOTEST_CMD  # 执行自动化脚本任务
            # cmd = 'sleep 5'
            result, error = yield call_subprocess(cmd)
        else:
            pass
            # self.write_message(ConstData.msg_fail)
            # self.write_message(u"You said: " + message)

    def on_close(self):
        """
        关闭连接时的动作
        """
        ApiTestsSocket.ws_client = None
