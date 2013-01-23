#!/usr/bin/env python
#-*- coding:utf-8 -*-

import datetime

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid

class Permission(Model):
    
    __storm_table__ = "permission"
    __export__ = [("user", "user_id"), ("granted_by", "granted_by_id"), "granted", "identifier"]
    __module__ = "goldmine.models.auth"
    __storm_primary__ = "user_id", "identifier"
    
    user_id = UUID()
    granted_by_id = UUID()
    granted =  DateTime(default_factory=datetime.datetime.now)
    identifier = Unicode()
    
    user = Reference(user_id, "auth.User.id")
    granted_by = Reference(granted_by_id, "auth.User.id")

