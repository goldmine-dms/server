#!/usr/bin/env python
#-*- coding:utf-8 -*-

import datetime

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid

class Sequence(Model):

    __storm_table__ = "dataset_sequence"
    __export__ = ["id", ("dataset", "dataset_id"), "index_type", "index_marker_type", "index_marker_location"]
    __module__ = "goldmine.models.dataset.sequence"

    id = UUID(primary=True, default_factory=generate_uuid)
    dataset_id = UUID()
    index_type_id = UUID()
    index_marker_type = Enum(map={"point": 1, "span": 2})
    index_marker_location = Enum(map={"center": 1, "start": 2, "end": 3})

    dataset = Reference(dataset_id, "dataset.Dataset.id")
    index_type = Reference(index_type_id, "dataset.sequence.Type.id")

    
    
    
