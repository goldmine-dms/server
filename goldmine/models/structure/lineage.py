#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *

class Lineage(Model):

    __storm_table__ = "lineage"
    __export__ = ["id", ("from_dataset", "from_id"), ("to_dataset", "to_id")]
    
    id = UUID(primary=True, default_factory=generate_uuid)
    from_id = UUID()
    to_id = UUID()
    from_dataset = Reference(from_id, "Dataset.id")
    to_dataset = Reference(to_id, "Dataset.id")   
    
