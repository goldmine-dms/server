#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *

class Datapoint(Model):

    __storm_table__ = "datapoints"
    __export__ = ["id", "y", "quality", ("parameter", "parameter_id"), ("measurement", "measurement_id")]
    
    id = UUID(primary=True, default_factory=generate_uuid)
    parameter_id = UUID()
    measurement_id = UUID()
    y = Float()
    quality = Float()
    parameter = Reference(parameter_id, "Parameter.id")
    measurement = Reference(measurement_id, "Measurement.id")   
    
