#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid


class Parameter(Model):

    __storm_table__ = "dataset_sequence_parameter"
    __export__ = ["id", "type", "uncertainty_value", "uncertainty_type", "storage", ("sequence", "sequence_id")]
    __module__ = "goldmine.models.dataset.sequence"

    id = UUID(primary=True, default_factory=generate_uuid)
    sequence_id = UUID()
    type_id = UUID()
    uncertainty_value = Float()
    uncertainty_type = Enum(map={"absolute": 1, "relative": 2})
    storage = Enum(map={"float": 1, "int": 2})
    sequence = Reference(sequence_id, "dataset.sequence.Sequence.id")
    type = Reference(type_id, "dataset.Type.id")

