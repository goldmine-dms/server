#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid

class Favorite(Model):
    
    __storm_table__ = "favorite"
    __export__ = ["name", ("user", "user_id"), "ref_id", "ref_type"]
    __module__ = "goldmine.models.auth"
    
    REFMAP = {
            "dataset": 1, 
            "datatype": 2,
            "study": 3,
            "activity": 4,
            "project": 5,
            "user": 6,
            "group": 7
        }

    id = UUID(primary=True, default_factory=generate_uuid)
    name = Unicode()

    user_id = UUID()
    ref_id = UUID()
    ref_type = Enum(map=REFMAP)

    user = Reference(user_id, "auth.User.id")
