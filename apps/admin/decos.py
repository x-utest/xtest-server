# 和权限相关的装饰器
import functools

from dtlib.web.constcls import ConstData

# from xt_base.document.acl_docs import UserGrpRel, Permissions


# def perm_check_future(method):
#     """
#     用户权限控制器,现在先不做细分吧,只区分是否是超管
#
#     :param method:
#     :return:
#     """
#
#     # todo:
#     async def wrapper(self, *args, **kwargs):
#         user = self.get_current_session_user()
#         group_rel = await UserGrpRel.objects.get(user=user)
#         """:type:UserGrpRel"""
#
#         if group_rel is None:
#             return ConstData.msg_forbidden
#
#         # todo 通过self获取接口路径
#         cur_control_name = '/accounts/xxxx/'
#         perm = await Permissions.objects.get(group=group_rel.group, control=cur_control_name)
#         """:type:Permissions"""
#
#         if perm is None:
#             return ConstData.msg_forbidden
#
#         if not perm.g_acc:
#             return ConstData.msg_forbidden
#
#         await method(*args, **kwargs)
#         pass
#
#     return wrapper


# def perm_check(method):
#     @functools.wraps(method)
#     async def wrapper(self, *args, **kwargs):
#         """
#         用户权限控制器
#         现在先不做细分吧,只区分是否是超管
#         :param self:
#         :param args:
#         :param kwargs:
#         :return:
#         """
#         user = self.get_current_session_user()  # 获取当前用户
#
#         grp_rel = await UserGrpRel.objects.get(user=user)
#         """:type:UserGrpRel"""
#         if grp_rel is None:
#             return ConstData.msg_forbidden
#
#         if grp_rel.g_code == 'admin':
#             return await method(self, *args, **kwargs)
#         else:
#             return ConstData.msg_forbidden
#
#     return wrapper


# def admin_required(method):
#     @functools.wraps(method)
#     async def wrapper(self, *args, **kwargs):
#         """
#         限制用户必须为超管
#         :param self:
#         :param args:
#         :param kwargs:
#         :return:
#         """
#         user = self.get_current_session_user()  # 获取当前用户
#
#         grp_rel = await UserGrpRel.objects.get(user=user)
#         """:type:UserGrpRel"""
#         if grp_rel is None:
#             return ConstData.msg_forbidden
#
#         if grp_rel.g_code == 'admin':
#             return await method(self, *args, **kwargs)
#         else:
#             return ConstData.msg_forbidden
#
#     return wrapper
