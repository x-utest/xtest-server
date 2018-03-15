from aiomotorengine import StringField, IntField, BooleanField, FloatField, DateTimeField, ReferenceField, ListField

from xt_base.document.source_docs import InfoAsset
from xt_base.document.base_docs import Project
from dtlib.aio.base_mongo import MyDocument
from dtlib.tornado.account_docs import Organization
from dtlib.tornado.base_docs import OrgDataBaseDocument


class ProjectDataDocument(OrgDataBaseDocument, MyDocument):
    """
    项目数据
    """
    # 数据归属
    project = ReferenceField(reference_document_type=Project)  # 测试数据所属的项目
    project_name = StringField()  # 项目名称,冗余

    async def set_project_tag(self, project):
        """
        打上项目标记
        :type project:Project
        :return:
        """

        organization = project.organization
        self.project = project
        self.project_name = project.project_name
        self.organization = organization
        self.org_name = organization.name


class ProjectFeedBack(ProjectDataDocument):
    """
    项目相关的问题反馈
    """

    msg = StringField()
    # images = ListField()  # 图片列表
    # todo 语音和视频
    label = StringField()  # 关于问题的标记
    status = IntField()  # 处理的状态码


class ServiceStatus(MyDocument):
    """
    服务器开放的服务状态
    """
    __collection__ = "service_status"

    info_asset = ReferenceField(reference_document_type=InfoAsset)  # 所属资产，信息资产
    port = IntField()  # 端口号
    protocol = StringField()  # 协议名称
    status = StringField()  # 状态
    version = StringField  # 版本


class ApiTestData(ProjectDataDocument):
    """
    测试数据统计表---因为性能问题,取消使用 2016-09-30
    """
    __collection__ = "api_test_data"

    was_successful = BooleanField()  # 是否是成功的
    total = IntField()
    failures = IntField()
    errors = IntField()
    skipped = IntField()
    run_time = StringField(max_length=1024)


class ApiTestDataNote(MyDocument):
    """
    api测试详细数据,只记录失败和错误---因为性能问题,取消使用 2016-09-30
    """
    __collection__ = "api_test_data_note"
    apitestdata_id = StringField(max_length=1024)
    test_case = StringField(max_length=1024)  # 出错测试用例
    explain = StringField(max_length=1024)  # 目的
    status = StringField(max_length=1024)  # 测试状态，失败或者错误
    note = StringField()  # 详细记录

    organization = ReferenceField(reference_document_type=Organization)  # 数据所属的组织


class UnitTestDataDetail(MyDocument):
    """
    api测试详细数据,只记录失败和错误--插入时没有使用
    """
    test_case = StringField(max_length=1024)  # 出错测试用例
    explain = StringField(max_length=1024)  # 目的
    status = StringField(max_length=1024)  # 测试状态，失败或者错误
    note = StringField()  # 详细记录


class UnitTestData(MyDocument):
    """
    测试数据统计表--插入时没有使用，没有使用ORM
    """
    __collection__ = "unit_test_data"

    pro_version = StringField(max_length=1024)  # 项目版本号:1.2.3.4
    was_successful = BooleanField()  # 是否是成功的
    total = IntField()
    failures = IntField()
    errors = IntField()
    skipped = IntField()
    run_time = FloatField()
    details = ListField(ReferenceField(UnitTestDataDetail))

    # 数据归属
    project = ReferenceField(reference_document_type=Project)  # 测试数据所属的项目
    project_name = StringField()  # 项目名称,冗余
    organization = ReferenceField(reference_document_type=Organization)  # 数据所属的组织


class PerformReport(MyDocument):
    """
    性能测试报告,已经作废,在bench中有专门的处理的了:2016-09-10
    waste
    """
    __collection__ = "perform_report"

    server_soft_ware = StringField(max_length=2048)
    server_host_name = StringField(max_length=2048)
    server_port = StringField(max_length=64)
    doc_path = StringField(max_length=2048)
    doc_length = IntField()  # 文档长度，bytes
    con_level = IntField()  # 并发量
    test_time_taken = FloatField()  # 消耗时间 seconds
    complete_req = IntField()  # 完成请求数
    failed_req = IntField()  # 失败请求数
    non_2xx_res = IntField()  # 非2xx请求数
    total_trans = IntField()  # 总传输数据量bytes
    html_trans = IntField()  # 总html传输数据量bytes
    req_per_sec = FloatField()  # 每秒请求量
    time_per_req = FloatField()  # 平均http请求响应时间:ms
    time_per_req_across = FloatField()  # 所有并发请求量耗时（平均事务响应时间）:ms
    trans_rate = FloatField()  # 每秒传输数据量,Kbytes/sec

    organization = ReferenceField(reference_document_type=Organization)  # 数据所属的组织


class SafetyTestReport(ProjectDataDocument):
    """
    安全测试报告
    """
    __collection__ = "safety_test_report"
    # project_name = StringField()  # 项目名,里面加上版本号,这个并不是具体的内部项目,和其它几种测试数据不同
    hack_tool = StringField()  # 用于hack的软件名称
    total_cnts = IntField()  # 总计次数
    success_cnts = IntField()  # 成功次数
    success_rate = FloatField()  # 成功率,冗余
    time_cycle = FloatField()  # 花费时间：s
    crack_rate = FloatField()  # 破解效率,冗余
    mark = StringField()  # 描述备注
    # organization = ReferenceField(reference_document_type=Organization)  # 组织


class ApiReqDelay(MyDocument):
    """测试接口的延时
    """
    __collection__ = "api_req_delay"

    domain = StringField(max_length=2048)  # ms，基准域
    path = StringField(max_length=2048)  # ms，接口路径及参数
    delay = FloatField()  # ms，请求时间
    http_status = IntField()  # http状态值

    # 数据归属
    project = ReferenceField(reference_document_type=Project)
    project_name = StringField()  # 项目名称,冗余
    organization = ReferenceField(reference_document_type=Organization)


class ExDataRecord(MyDocument):
    """
    实验数据的记录表
    """

    __collection__ = "ex_data_record"

    # --------------数据状态值记录-----------
    record_status = StringField(max_length=64)  # 数据的状态：reported,filted,experiment
    # --------------数据发现和登记期-----------
    custom_name = StringField(max_length=256)  # 用户名称
    captcha_id = StringField(max_length=64)
    event_start_time = DateTimeField()  # weblog产生开始时间
    event_end_time = DateTimeField()  # weblog产生结束时间
    event_reporter = StringField(max_length=256)  # 事件汇报人
    event_report_time = DateTimeField()  # 事件汇报时间
    track_class = StringField(max_length=64)
    js_version = StringField(max_length=16)
    js_tag_page = StringField(max_length=2048)  # 在bitbucket或者tower中的当前版本的修改标记
    css_version = StringField(max_length=16)
    css_tag_page = StringField(max_length=2048)  # 在bitbucket或者tower中的当前版本的修改标记
    # --------------数据过滤的采集备案期-----------
    data_collection_name = StringField(max_length=256)
    producers = StringField(max_length=256)
    ex_user = StringField(max_length=256)  # 数据收集人
    action_time = DateTimeField()  # 数据备案时间
    # event_time = DateTimeField()
    file_name = StringField(max_length=64)
    file_path = StringField(max_length=2048)  # 实验数据文件所在路径,以FTP的方式来共享
    file_size = IntField()
    record_cnt = IntField()  # 记录的数目
    # --------------数据实验期-----------
    researcher = StringField(max_length=256)  # 数据实验人
    researche_time = DateTimeField()  # 数据实验时间
    research_result = StringField(max_length=10240)  # 验证处理结果
    # experiment_id= Refer


class CurtainExData(MyDocument):
    """
    Curtain项目的测试数据
    """
    # answer = ListField()
    # track_data = ListField()
    action_user = StringField(max_length=256)


class LimitTestData(MyDocument):
    """
    测试数据统计表
    """
    __collection__ = "limit_test_data"

    # id = ObjectId()
    was_successful = BooleanField()  # 是否是成功的
    total = IntField()
    failures = IntField()
    errors = IntField()
    skipped = IntField()
    run_time = StringField(max_length=1024)

    organization = ReferenceField(reference_document_type=Organization)  # 数据所属的组织


class LimitTestDataNote(MyDocument):
    """
    api测试详细数据,只记录失败和错误(作废-2016-11-23)
    """
    __collection__ = "limit_test_data_note"
    limittestdata_id = StringField(max_length=1024)
    test_case = StringField(max_length=1024)  # 出错测试用例
    explain = StringField(max_length=1024)  # 目的
    status = StringField(max_length=1024)  # 测试状态，失败或者错误
    note = StringField()  # 详细记录

    organization = ReferenceField(reference_document_type=Organization)  # 数据所属的组织


class UnitPenetrationTest(MyDocument):
    """
    渗透测试详细信息
    """
    test_case = StringField(max_length=1024)  # 测试目的
    result = StringField(max_length=1024)  # 结果


class PenetrationTestData(ProjectDataDocument):
    """
    渗透测试详情
    """
    __collection__ = "penetration_test_data"
    start_time = StringField()
    use_time = FloatField()
    note = StringField()
    # project = ReferenceField(reference_document_type=Project)  # 测试数据所属的项目
    # project_name = StringField()  # 项目名称,冗余
    # organization = ReferenceField(reference_document_type=Organization)  # 数据所属的组织


class PenetrationTestDataNote(MyDocument):
    """
    渗透测试详情
    """
    __collection__ = "penetration_test_data_note"
    penetration_id = StringField(max_length=1024)
    ip = StringField(max_length=1024)
    details = ListField(ReferenceField(UnitPenetrationTest))
    # SSHRootEmptyPassword = StringField(max_length=1024)
    # RedisEmptyPassword = StringField(max_length=1024)
    # MongoEmptyPassword = StringField(max_length=1024)
    organization = ReferenceField(reference_document_type=Organization)  # 数据所属的组织


class ProxyipTestData(MyDocument):
    """
    爆破测试
    """
    __collection__ = "proxyip_test_data"
    remoteip = StringField(max_length=1024)
    originalip = StringField(max_length=1024)
    proxyip = StringField(max_length=1024)

    organization = ReferenceField(reference_document_type=Organization)  # 数据所属的组织


class FeedbackMsg(MyDocument):
    """
    feedback
    """

    __collection__ = 'feedback_msg'
    file_path = StringField()  # 文件路径
    msg = StringField()  # msg
