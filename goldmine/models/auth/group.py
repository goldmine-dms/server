#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid

class Group(Model):

    __export__ = ["id", ("parent", "parent_id"), "name"]
    
    id = UUID(primary=True, default_factory=generate_uuid)
    parent_id = UUID()
    parent = Reference(parent_id, "auth.Group.id")
    name = Unicode()


class GroupMember(Model):
    
    __storm_table__ = "group_member"
    
    user_id = UUID()
    group_id = UUID()
    
    user = Rreference(user_id, "auth.User.id")
    group = Rreference(user_id, "auth.Group.id")
    
