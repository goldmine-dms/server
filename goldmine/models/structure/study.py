#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid

class Study(Model):

    __export__ = ["id", "name", "description", ("activities", None), ("datasets", None), ("owner", "owner_id")]
    
    id = UUID(primary=True, default_factory=generate_uuid)
    name = Unicode()
    description = Unicode()
    owner_id = UUID() 
    
    activities = ReferenceSet(id, "structure.ActivityStudy.study_id", "structure.ActivityStudy.activity_id", "structure.Activity.id")
    datasets = ReferenceSet(id, "dataset.Dataset.study_id")
    owner = Reference(owner_id, "auth.User.id")
