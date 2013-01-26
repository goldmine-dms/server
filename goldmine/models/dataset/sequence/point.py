#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid


class Point(Model):

    __storm_table__ = "dataset_sequence_point"
    __export__ = ["id", "value", "uncertainty_value", "parameter_index", ("index", "index_id")] #("parameter", "parameter_index"),
    __module__ = "goldmine.models.dataset.sequence"

    id = UUID(primary=True, default_factory=generate_uuid)
    parameter_index = Int()
    index_id = UUID()
    value = Float()
    uncertainty_value = Float()
    
    #parameter = Reference(parameter_index, "dataset.sequence.Parameter.index")
    index = Reference(index_id, "dataset.sequence.Index.id")   
    
