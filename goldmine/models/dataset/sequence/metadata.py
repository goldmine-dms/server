#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid


class Metadata(Model):

    __storm_table__ = "dataset_sequence_metadata"
    __export__ = ["id", ("metadata", "metadata_id"), ("sequence", "sequence_id"), ("parameter", "parameter_id"), ("index", "index_id"), ("point", "point_id")]
    
    id = UUID(primary=True, default_factory=generate_uuid)
    
    metadata_id = UUID()
    sequence_id = UUID()
    parameter_id = UUID()
    index_id = UUID()
    point_id = UUID()
    
    metadata = Reference(metadata_id, "metadata.Metadata.id")
    dataset = ReferenceSet(sequence_id, "dataset.sequence.Sequence.id", "dataset.sequence.Sequence.dataset_id", "dataset.Dataset.id")   
    sequence = Reference(sequence_id, "dataset.sequence.Sequence.id")
    parameter = Reference(parameter_id, "dataset.sequence.Parameter.id")
    index = Reference(index_id, "dataset.sequence.Index.id")   
    point = Reference(point_id, "dataset.sequence.Point.id")   

