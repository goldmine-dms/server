#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid

class Location(Model):

    __export__ = ["longitude", "latitude", "radius", "elevation"]
    __module__ = "goldmine.models.structure"
    __storm_table__ = "location"
    
    id = UUID(primary=True, default_factory=generate_uuid)
    longitude = Float()
    latitude = Float()
    radius = Float()
    elevation = Int()
    
    @staticmethod
    def from_struct(loc):
        location = Location()
        if not "longitude" in loc or not "latitude" in loc:
            raise TypeError("Both longitude and latitude must be present in location structure")
        for attr in ["longitude", "latitude", "radius", "elevation"]:
            if attr in loc:
                setattr(location, attr, loc[attr])
        return location

