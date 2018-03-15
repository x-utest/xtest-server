import os

from tornado.web import StaticFileHandler

# from config import *
from config import settings, BASE_DIR
from dtlib.tornado.tools import get_apps_url

urls = get_apps_url(BASE_DIR)

try:
    from xt_wechat.urls import url
    # TODO: set online flag.
    urls += url
except:
    pass

urls += [
    (r"/favicon.ico", StaticFileHandler, {"path": "/static/favicon.ico"}),
    (r"/js/(.*)", StaticFileHandler, {"path": os.path.join(settings['static_path'], 'js')}),
    (r"/css/(.*)", StaticFileHandler, {"path": os.path.join(settings['static_path'], 'css')}),
    (r"/img/(.*)", StaticFileHandler, {"path": os.path.join(settings['static_path'], 'img')}),
    (r"/content/(.*)", StaticFileHandler, {"path": os.path.join(settings['static_path'], 'content')}),

]

# todo 后续写成 include的方式，更直观
