from django.test import TestCase

# Create your tests here.
import re

ret = re.match('/users/', "/users/delete/9")
print(ret)  # 匹配成功：<_sre.SRE_Match object; span=(0, 7), match='/users/'>

# 这两个字段一个是查询、一个是删除权限，应该是不匹配成功的
ret = re.match('^/users/$', "/users/delete/9")
print(ret)  # 匹配失败：None



l = ['/users/', '/users/add', '/users/delete/(\d+)', '/users/edit/(\d+)']

c_path = "/users/delete/9"


flag = False
for permission in l:
    permission = "^%s$" % permission
    ret = re.match(permission, c_path)
    if ret:
        # 匹配成功有一个对象
        flag = True


if flag:
    print("success")
