from apps.project.handlers import *
from dtlib import filetool

app_path = filetool.get_parent_folder_name(__file__)  # set the relative path in one place

url = [

    (r"/%s/create-test-project/" % app_path, CreateTestProject),  # 创建项目
    (r"/%s/update-test-project/" % app_path, UpdateTestProject),  # 更新项目
    (r"/%s/delete-test-project/" % app_path, DeleteTestProject),  # 删除项目
    (r"/%s/list-projects/" % app_path, ListProjects),  # 本组织的所有项目

    (r"/%s/xtest-client-config/" % app_path, ListProjectsNote),  # 根据project——id查找app-id

    (r"/%s/read-projects-record/" % app_path, ReadProjectsRecord),  # 根据project—id查找30次的构建情况
    (r"/%s/get-tags/" % app_path, GetProjectTags),  # 根据project—id查找30次的构建情况

]
