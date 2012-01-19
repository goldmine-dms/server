#!/usr/bin/env python
#-*- coding:utf-8 -*-

import datetime

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid

class Lineage(Model):

    __export__ = ["id", ("from_dataset", "from_dataset_id"), ("to_dataset", "to_dataset_id"), "fork_type", "forked", "forked_by"]
    __module__ = "goldmine.models.structure"
    
    id = UUID(primary=True, default_factory=generate_uuid)
    from_dataset_id = UUID()
    to_dataset_id = UUID()
    fork_type = Enum(map={"corrected": 1, "derived": 2})
    forked = DateTime(default_factory=datetime.datetime.now)
    forked_by_id = UUID()
    
    from_dataset = Reference(from_dataset_id, "dataset.Dataset.id")
    to_dataset = Reference(to_dataset_id, "dataset.Dataset.id")   
    forked_by = Reference(forked_by_id, "auth.User.id")   
