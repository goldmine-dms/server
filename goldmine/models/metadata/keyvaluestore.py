#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *

class MetadataParams(Model):

    __storm_table__ = "metadata_params"
    __export__ = ["id", "key", "value"]
    
    id = UUID(primary=True, default_factory=generate_uuid)
    metadata_id = UUID()
    key = Unicode()
    value = Float()
