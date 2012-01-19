#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid

class Annotation(Model):

    __storm_table__ = "metadata_annotation"
    __export__ = ["id", "annotation"]
    
    id = UUID(primary=True, default_factory=generate_uuid)
    metadata_id = UUID()
    annotation = Unicode()
    
