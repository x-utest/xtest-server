from dtlib import filetool

from apps.testdata.handlers import *

app_path = filetool.get_parent_folder_name(__file__)  # 'apis'  # set the relative path in one place

url = [
    # 测试结果插入数据


    (r"/%s/api-auth/" % app_path, ApiAuth),
    (r"/%s/api-auth-out/" % app_path, ApiAuthout),

    # api_auth纯接口区jsonp，不涉及UI,
    (r"/%s/create-perform-report/" % app_path, CreatePerformReport),  # 服务端性能测试报告
    (r"/%s/create-safety-test-report/" % app_path, CreateSafetyTestReport),  # 安全数据
    (r"/%s/create-api-req-delay/" % app_path, CreateApiReqDelay),  # 模拟浏览器器请求的响应时间
    (r"/%s/create-penetration-test-data/" % app_path, CreatePenetrationReport),  # 插入渗透测试数据
    (r"/%s/create-penetration-test-data-note/" % app_path, CreatePenetrationReportNote),  # 插入渗透测试数据详情
    (r"/%s/create-proxyip-test-data/" % app_path, CreateProxyipReport),  # 插入代理ip测试数据

    (r"/%s/create-test-data/" % app_path, CreateUnitTestData),  # 创建完整的测试数据--自动化高频接口
    (r"/%s/list-test-data/" % app_path, ListUnitTestData),  # 显示分页信息,不使用ORM
    (r"/%s/get-one-test-data/" % app_path, GetOneUnitTestData),  # 显示一个数据信息

    # login_auth分页信息显示-jsonp
    (r"/%s/read-server-api-testdata/" % app_path, ListApiTestData),  # 接口测试
    (r"/%s/read-safety-testdata/" % app_path, ListSafetyTestData),  # 安全测试
    (r"/%s/read-performance-testdata/" % app_path, ListPerformanceTestData),  # 压力测试
    (r"/%s/read-api-req-delay-testedata/" % app_path, ListApiReqDelay),  # 响应时间的显示
    (r"/%s/read-penetration-test-data/" % app_path, ReadPenetrationReport),  # 读取爆破测试数据
    (r"/%s/read-penetration-test-data-note/" % app_path, ReadPenetrationReportNote),  # 读取爆破测试数据
    (r"/%s/read-proxyip-test-data/" % app_path, ReadProxyipReport),  # 读取代理ip测试数据

    (r"/%s/delete-test-data/" % app_path, DeleteTestData),  # 删除接口测试数据

    (r"/%s/feedback/" % app_path, CreateFeedback),  #
    (r"/%s/feedback-list/" % app_path, FeedbackList),  #

]
