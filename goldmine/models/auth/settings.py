#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid

class Settings(Model):

    __storm_table__ = "user_settings"
    __export__ = ["id", "setting", "value"]
    __module__ = "goldmine.models.auth.settings"
    
    id = UUID(primary=True, default_factory=generate_uuid)
    user_id = UUID()
    user = Reference(user_id, "auth.User.id")
    setting = Unicode()
    value = Unicode()
  
