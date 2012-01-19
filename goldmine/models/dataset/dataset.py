#!/usr/bin/env python
#-*- coding:utf-8 -*-

import datetime

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid

class Dataset(Model):

    __storm_table__ = "dataset"
    __export__ = ["id", ("study", "study_id"), "created", "closed", "description", "curation_status", "curated", ("curated_by", "curated_by_id"), ("parents", None), ("children", None)]
    
    id = UUID(primary=True, default_factory=generate_uuid)
    type = Unicode()
    study_id = UUID()
    
    created = DateTime(default_factory=datetime.datetime.now)
    closed = DateTime()
    
    description = Unicode()
    curation_status = Enum(map={"none": 1, "proposed": 2, "curated": 3})
    curated_by_id = UUID()
    curated = DateTime()
    
    children = ReferenceSet(id, "structure.Lineage.from_dataset_id", "structure.Lineage.to_dataset_id", "dataset.Dataset.id")
    parents = ReferenceSet(id, "structure.Lineage.to_dataset_id", "structure.Lineage.from_dataset_id", "dataset.Dataset.id")
    study = Reference(study_id, "structure.Study.id")
    curated_by = Reference(curated_by_id, "auth.User.id")
    
    
    
