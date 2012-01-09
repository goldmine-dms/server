#!/usr/bin/env python
#-*- coding:utf-8 -*-

import datetime

from storm.locals import *
from goldmine.models import *

class Dataset(Model):

    __storm_table__ = "datasets"
    __export__ = ["id", ("study", "study_id"), "xtype", "markertype", "markerlocation", "params", "created", "closed", "description", ("parents", None), ("children", None)]
    
    id = UUID(primary=True, default_factory=generate_uuid)
    study_id = UUID()
    xtype_id = UUID()
    markertype = Enum(map={"span": 1, "point": 2}) 
    markerlocation = Enum(map={"start": 1, "center": 2, "end": 3, "na": 4})
    created = DateTime(default_factory=datetime.datetime.now)
    closed = DateTime()
    description = Unicode()
    
    children = ReferenceSet(id, "Lineage.from_id", "Lineage.to_id", "Dataset.id")
    parents = ReferenceSet(id, "Lineage.to_id", "Lineage.from_id", "Dataset.id")

    params = ReferenceSet(id, "Parameter.dataset_id")
    study = Reference(study_id, "Study.id")
    xtype = Reference(xtype_id, "Type.id")

