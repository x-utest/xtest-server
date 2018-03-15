"""
分享link
"""
from aiomotorengine import StringField, IntField
from dtlib.tornado.base_docs import OrgUserDataDocument

from xt_base.document.base_docs import ProjectBaseDocument


# todo 后面都要加上项目的名称的冗余

class ShareTestReport(OrgUserDataDocument, ProjectBaseDocument):
    """
    分享测试报告,只有拥有此share的ID流水号的，就可以访问此报告信息,
    永久性的
    """

    __collection__ = 'share_test_report'
    rep_id = StringField()  # 报告的流水号
    stoken = StringField()  # 访问此报告时所需要的token串号，share token
    cnt = IntField()  # 被访问的次数
    mark = StringField()  # 关于此分享的备注信息
    # project = ReferenceField(reference_document_type=Project)  # 测试数据所属的项目
    # project_name = StringField()  # 项目名称,冗余



class ShareProjectReport(OrgUserDataDocument, ProjectBaseDocument):
    """
    分享测试项目报告,只有拥有此share的ID流水号的，就可以访问此报告信息,
    永久性的
    """
    __collection__ = 'share_project_report'
    pro_id = StringField()  # 测试项目id
    stoken = StringField()  # 访问此报告时所需要的token串号，share token
    cnt = IntField()  # 被访问的次数
    mark = StringField()  # 关于此分享的备注信息
    # project = ReferenceField(reference_document_type=Project)  # 测试数据所属的项目
    # project_name = StringField()  # 项目名称,冗余