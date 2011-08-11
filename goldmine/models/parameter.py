#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *

class Parameter(Model):

    __storm_table__ = "parameters"
    __export__ = ["id", "ytype", ("dataset", "dataset_id")]
    
    id = UUID(primary=True, default_factory=generate_uuid)
    dataset_id = UUID()
    ytype_id = UUID()
    dataset = Reference(dataset_id, "Dataset.id")
    ytype = Reference(ytype_id, "Type.id")

