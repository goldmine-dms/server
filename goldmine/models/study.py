#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *

class Study(Model):

    __storm_table__ = "studies"
    __export__ = ["id", "name", "description", ("cores", None), ("datasets", None), ("owner", "owner_id")]
    
    id = UUID(primary=True, default_factory=generate_uuid)
    name = Unicode()
    description = Unicode()
    owner_id = UUID() 
    
    cores = ReferenceSet(id, "CoreStudy.study_id", "CoreStudy.core_id", "Core.id")
    datasets = ReferenceSet(id, "Dataset.study_id")
    owner = Reference(owner_id, "User.id")
