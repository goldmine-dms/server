#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid

class Group(Model):

    __storm_table__ = "group"
    __export__ = ["id", ("parent", "parent_id"), ("children", None), ("members", None), "name"]
    __module__ = "goldmine.models.auth"
    
    id = UUID(primary=True, default_factory=generate_uuid)
    parent_id = UUID()
    parent = Reference(parent_id, "auth.Group.id")
    children = ReferenceSet(id, "auth.Group.parent_id")
    members = ReferenceSet(id, "auth.GroupMember.group_id", "auth.GroupMember.user_id", "auth.User.id")
    name = Unicode()


class GroupMember(Model):
    
    __storm_table__ = "group_member"
    __storm_primary__ = "user_id", "group_id"
    __module__ = "goldmine.models.auth"
    __export__ = [("user", "user_id"), ("group", "group_id")]


    user_id = UUID()
    group_id = UUID()
    
    user = Reference(user_id, "auth.User.id")
    group = Reference(group_id, "auth.Group.id")
    


class StudyGroup(Model):
    
    __storm_table__ = "study_group"
    __module__ = "goldmine.models.auth"
    __storm_primary__ = "study_id", "group_id"

    __export__ = [("study", "study_id"), ("group", "group_id"), "role"]

    ROLEMAP = {"read": 1, "write": 2, "admin": 3}
    
    study_id = UUID()
    group_id = UUID()
    role = Enum(map=ROLEMAP)

    study = Reference(study_id, "structure.Study.id")
    group = Reference(group_id, "auth.Group.id")
    

