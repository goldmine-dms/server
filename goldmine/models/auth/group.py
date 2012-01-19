#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid

class Group(Model):

    __export__ = ["id", ("parent", "parent_id"), "name"]
    __module__ = "goldmine.models.auth"
    
    id = UUID(primary=True, default_factory=generate_uuid)
    parent_id = UUID()
    parent = Reference(parent_id, "auth.Group.id")
    name = Unicode()


class GroupMember(Model):
    
    __storm_table__ = "group_member"
    __storm_primary__ = "user_id", "group_id"
    __module__ = "goldmine.models.auth"
    
    user_id = UUID()
    group_id = UUID()
    
    user = Reference(user_id, "auth.User.id")
    group = Reference(user_id, "auth.Group.id")
    
