#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *

class Measurement(Model):

    __storm_table__ = "measurements"
    __export__ = ["id", "x", "span"]
    
    id = UUID(primary=True, default_factory=generate_uuid)
    dataset_id = UUID()
    x = Float()
    span = Float()
    dataset = Reference(dataset_id, "Dataset.id")

