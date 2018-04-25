import logging
import os
import sys

from dtlib.dbtool import DbSetting

app_version = '4.18.4.24.1'  # 项目版本号
test_token = '1234'  # 用于超级管理员调用url的简单的token

# if you use tornado project,this returns the root of the project
BASE_DIR = os.path.abspath(os.path.curdir)
debug_mode = False  # 是否是调试模式

settings = {
    "cookie_secret": "42233434",
    # 'xsrf_cookies':True,
    "debug": False,  # 非调试模式
    "static_path": os.path.join(BASE_DIR, "static"),  # 静态文件目录
    # "login_url":"/",
    "template_path": os.path.join(BASE_DIR, "static/templates"),  # 模板目录
}

HTTP_PORT = 8011  # 启动本app的端口
SERVER_PROCESS = 0  # 设置进程数，0表示利用所有的CPU核心

# 根据环境变量，切换开发态和生产态
try:
    docker_flag = os.environ.get('DOCKER', "")
    # TODO: add online config.
    if docker_flag == '1':
        mongo_host = 'mongo'
        print('Run in docker!')
    else:
        mongo_host = '127.0.0.1'
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise

# ======Mongodb===
mongodb_cfg = DbSetting(
    alias='default',
    host=mongo_host,
    port=27017,
    db_name='xtest',
    user_name='xtest',
    user_pwd='xtest@2018',
    max_connections=10
)

LOGGING_LEVEL = logging.ERROR  # 日志输出的级别
LOGGING_STREAM = '/dev/stdout'  # 重定向到控制台

AUTOTEST_CMD = 'python /api-test-template/run.py'  # 自动化测试脚本

if __name__ == '__main__':
    # BASE_DIR = os.path.abspath('.')
    # print BASE_DIR
    pass
