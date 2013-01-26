#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid


class Metadata(Model):

    __storm_table__ = "dataset_sequence_metadata"
    __export__ = ["id", ("metadata", "metadata_id"), ("sequence", "sequence_id"), "parameter_index", ("index", "index_id"), ("point", "point_id")] # ("parameter", "parameter_index"),
    __module__ = "goldmine.models.dataset.sequence"

    id = UUID(primary=True, default_factory=generate_uuid)
    
    metadata_id = UUID()
    sequence_id = UUID()
    parameter_index = Int()
    index_id = UUID()
    point_id = UUID()
    
    metadata = Reference(metadata_id, "metadata.Metadata.id")
    dataset = ReferenceSet(sequence_id, "dataset.sequence.Sequence.id", "dataset.sequence.Sequence.dataset_id", "dataset.Dataset.id")   
    sequence = Reference(sequence_id, "dataset.sequence.Sequence.id")
    # FIXME  
    # parameter = Reference(parameter_index, "dataset.sequence.Parameter.index")
    index = Reference(index_id, "dataset.sequence.Index.id")   
    point = Reference(point_id, "dataset.sequence.Point.id")   

