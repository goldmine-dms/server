#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *

class Site(Model):

    __storm_table__ = "sites"
    __export__ = ["id", "name", "longitude", "latitude", "elevation", "description", "cores"]
    
    id = UUID(primary=True, default_factory=generate_uuid)
    name = Unicode()
    longitude = Float()
    latitude = Float()
    elevation = Float()
    description = Unicode()
    cores = ReferenceSet(id, "Core.site_id")
