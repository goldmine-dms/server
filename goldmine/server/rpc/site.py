#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Site functions
"""

from goldmine import *
from goldmine.db import db
from goldmine.models import *

from goldmine.server import needauth, rstolist, noempty, uuid
from goldmine.server.service import Unauthorized

@needauth
def get(sid, user):
    # FIXME: Add authentication
    sid = uuid(sid)
        
    return noempty(db().get(Site, sid))
    
@needauth
def listing(search, user):
    # FIXME: Add authentication
    if search is None or search == "":
        rs = db().find(Site).order_by(Site.name)
    else:
        rs = db().find(Site, Site.name == search).order_by(Site.name)
        
    return rstolist(rs)
    
@needauth  
def new(name, latitude, longitude, elevation, description, user):
    # FIXME: Add authentication
    s = Site()
    s.name = name
    s.latitude = latitude
    s.longitude = longitude
    s.elevation = elevation
    s.description = description
    return db().add(s)
