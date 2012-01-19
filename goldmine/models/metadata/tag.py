#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid

class Tag(Model):

    __storm_table__ = "metadata_tag"
    __export__ = ["id", "tag"]
    
    id = UUID(primary=True, default_factory=generate_uuid)
    metadata_id = UUID()
    tag = Unicode()
    
