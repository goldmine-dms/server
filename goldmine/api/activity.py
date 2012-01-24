#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Site functions
"""
"""
from goldmine import *
from goldmine.db import db
from goldmine.models import *

from goldmine.server import needauth, rstolist, noempty, uuid
from goldmine.server.service import Unauthorized

@needauth
def get(cid, user):
    # FIXME: Add authentication
    cid = uuid(cid)
    
    return noempty(db().get(Core, cid)) 

@needauth  
def new(site_id, name, latitude, longitude, elevation, description, user):
    # FIXME: Add authentication
    site_id = uuid(site_id)
    
    c = Core()
    c.site = db().get(Site, site_id)
    c.name = name
    c.latitude = latitude
    c.longitude = longitude
    c.elevation = elevation
    c.description = description
    return db().add(c)
"""
