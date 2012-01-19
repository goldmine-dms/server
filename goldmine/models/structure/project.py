#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid

class Project(Model):

    __export__ = ["id", "name", "description", "location", "activities"]
    __module__ = "goldmine.models.structure"
    
    id = UUID(primary=True, default_factory=generate_uuid)
    name = Unicode()
    location_id = UUID()
    description = Unicode()
    location = Reference(location_id, "structure.Location.id")
    activities = ReferenceSet(id, "structure.Activity.project_id")
