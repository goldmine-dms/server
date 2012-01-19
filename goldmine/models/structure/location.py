#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid

class Location(Model):

    __export__ = ["id", "longitude", "latitude", "radius", "elevation"]
    
    id = UUID(primary=True, default_factory=generate_uuid)
    longitude = Float()
    latitude = Float()
    radius = Float()
    elevation = Int()

