#!/usr/bin/env python
#-*- coding:utf-8 -*-

import datetime

from storm.locals import *
from goldmine.models import *

class Metadata(Model):

    __storm_table__ = "metadata"
    __export__ = ["id", "annotation", "params", "created", 
                  "creator", "measurement", "datapoint"]
    
    id = UUID(primary=True, default_factory=generate_uuid)
    dataset_id = UUID()
    parameter_id = UUID()
    measurement_id = UUID()
    datapoint_id = UUID()

    dataset = Reference(dataset_id, "Dataset.id")
    parameter = Reference(parameter_id, "Parameter.id")
    measurement = Reference(measurement_id, "Measurement.id")
    datapoint = Reference(datapoint_id, "Datapoint.id")

    created = DateTime(default_factory=datetime.datetime.now)
    created_by = UUID()
    creator = Reference(created_by, "User.id")
    
    annotation = Unicode()
    params = ReferenceSet(id, "MetadataParams.metadata_id")
