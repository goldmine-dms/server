#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid

class Type(Model):

    __storm_table__ = "dataset_sequence_type"
    __export__ = ["id", "name", "unit", "description"]
    
    id = UUID(primary=True, default_factory=generate_uuid)
    name = Unicode()
    unit = Unicode()
    storage = Enum(map={"float": 1, "int": 2})
    description = Unicode()
    parameters_with_type = ReferenceSet(id, "dataset.sequence.Parameter.type_id", "dataset.sequence.Parameter.sequence_id", "dataset.sequence.Sequence.id")  
    index_with_type = ReferenceSet(id, "dataset.sequence.Sequence.type_id")
