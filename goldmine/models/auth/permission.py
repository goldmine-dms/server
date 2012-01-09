#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid

class Permission(Model):
    
    __export__ = ["id", ("study", "study_id"), ("group", "group_id"), "name", "identifier"]
    
    study_id = UUID()
    group_id = UUID()
    identifier = Unicode()
    
    study = Rreference(user_id, "structure.Study.id")
    group = Rreference(user_id, "auth.Group.id")
