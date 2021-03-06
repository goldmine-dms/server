#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid

class Study(Model):
    
    __storm_table__ = "study"
    __export__ = ["id", "name", "description", ("activities", None), ("datasets", None), ("owner", "owner_id"), ("access", None)]
    __module__ = "goldmine.models.structure"
    
    id = UUID(primary=True, default_factory=generate_uuid)
    name = Unicode()
    description = Unicode()
    owner_id = UUID() 
    
    activities = ReferenceSet(id, "structure.ActivityStudy.study_id", "structure.ActivityStudy.activity_id", "structure.Activity.id")
    datasets = ReferenceSet(id, "dataset.Dataset.study_id")
    owner = Reference(owner_id, "auth.User.id")
    access = ReferenceSet(id, "auth.StudyGroup.study_id")
