#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid

class Index(Model):

    __storm_table__ = "dataset_sequence_index"
    __export__ = ["id", "location", "span"]
    __module__ = "goldmine.models.dataset.sequence"
    
    id = UUID(primary=True, default_factory=generate_uuid)
    sequence_id = UUID()
    location = Float()
    span = Float()
    sequence = Reference(sequence_id, "dataset.sequence.Sequence.id")

