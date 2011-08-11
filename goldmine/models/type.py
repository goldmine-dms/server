#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *

class Type(Model):

    __storm_table__ = "types"
    __export__ = ["id", "name", "species", "classification", "unit", "description"]
    
    id = UUID(primary=True, default_factory=generate_uuid)
    name = Unicode()
    species = Unicode()
    classification = Enum(map={"main": 1, "support": 2, "error": 3, "timescale": 4})
    storage = Enum(map={"float": 1, "int": 2})
    unit = Unicode()
    description = Unicode()
    dataset_ytype = ReferenceSet(id, "Parameter.ytype_id", "Parameter.dataset_id", "Dataset.id")  
    dataset_xtype = ReferenceSet(id, "Dataset.xtype_id")
