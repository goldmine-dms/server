#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid


class Point(Model):

    __storm_table__ = "dataset_sequence_point"
    __export__ = ["id", "value", "uncertainty_value", "uncertainty_type", ("parameter", "parameter_id"), ("index", "index_id")]
    
    id = UUID(primary=True, default_factory=generate_uuid)
    parameter_id = UUID()
    index_id = UUID()
    value = Float()
    uncertainty_value = Float()
    uncertainty_type = Enum(map={"absolute": 1, "relative": 2})
    
    parameter = Reference(parameter_id, "dataset.sequence.Parameter.id")
    index = Reference(index_id, "dataset.sequence.Index.id")   
    
