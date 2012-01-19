#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid

class Activity(Model):

    __export__ = ["id", "name", "description", "location", ("project", "project_id"), ("studies", None)]
    __module__ = "goldmine.models.structure"
    
    id = UUID(primary=True, default_factory=generate_uuid)
    name = Unicode()
    description = Unicode()
    project_id = UUID()
    location_id = UUID()
    project = Reference(project_id, "structure.Project.id")
    location = Reference(location_id, "structure.Location.id")
    studies = ReferenceSet(id, "structure.ActivityStudy.core_id", "structure.ActivityStudy.study_id", "structure.Study.id")
