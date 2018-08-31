# -*- coding:utf-8 -*-
__author__ = 'Qiushi Huang'

from stark.service.stark import site,ModelStark
from .models import *


class UserConfig(ModelStark):
    list_display = ["name", "roles"]


site.register(User, UserConfig)


class RoleConfig(ModelStark):
    list_display = ["title", "permissions"]


site.register(Role, RoleConfig)


class PermissionConfig(ModelStark):
    list_display = ["id", "title", "url", "group", "action"]


site.register(Permission, PermissionConfig)

site.register(PermissionGroup)
