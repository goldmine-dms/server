#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid

class Type(Model):

    __storm_table__ = "dataset_type"
    __export__ = ["id", "name", "unit", "description", "uniname"]
    __module__ = "goldmine.models.dataset"

    id = UUID(primary=True, default_factory=generate_uuid)
    name = Unicode()
    unit = Unicode()
    description = Unicode()
    uniname = Unicode()
    
    
    def signature(self):
        return "%s (%s)" % (self.name, self.unit)
