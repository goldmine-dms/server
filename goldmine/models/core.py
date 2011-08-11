#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *

class Core(Model):

    __storm_table__ = "cores"
    __export__ = ["id", "name", "longitude", "latitude", "elevation", "description", ("site", "site_id"), ("studies", None)]
    
    id = UUID(primary=True, default_factory=generate_uuid)
    name = Unicode()
    site_id = UUID()
    longitude = Float()
    latitude = Float()
    elevation = Float()
    description = Unicode()
    site = Reference(site_id, "Site.id")
    studies = ReferenceSet(id, "CoreStudy.core_id", "CoreStudy.study_id", "Study.id")
