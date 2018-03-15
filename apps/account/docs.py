"""

"""
from aiomotorengine import BooleanField, StringField

from dtlib.tornado.base_docs import UserBaseDocument


class LanAppUser(UserBaseDocument):
    """
    内网应用的用户
    """
    __collection__ = "lan_app_users"
    is_active = BooleanField()

