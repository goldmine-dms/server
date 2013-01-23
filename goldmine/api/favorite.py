#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Favorite functions
"""

import string

from storm.locals import *

from goldmine import *
from goldmine.db import db
from goldmine.models import *
from goldmine.controller import *

@apimethod.auth
def get(name):
    rs = db().find(auth.Favorite, auth.Favorite.name == name, auth.Favorite.user == user)
    return not_empty(rs.one())

@apimethod.auth
def get_by_reference(id, type):
    id = uuid(id)
    rs = db().find(auth.Favorite, 
            auth.Favorite.ref_id == id, 
            auth.Favorite.ref_type == type, 
            auth.Favorite.user == user)
    return rs.one()
    
@apimethod.auth
def all():
    rs = db().find(auth.Favorite, auth.Favorite.user == user).order_by(auth.Favorite.name)
    return rs_to_list(rs)
    
@apimethod.auth
def add(name, reference_id, reference_type="dataset"):

    if reference_type not in auth.Favorite.REFMAP:
        raise TypeError("Invalid reference type")

    if name != valid_name(name):
        raise TypeError("Invalid name, no spaces or special characters!")

    favorite = auth.Favorite()
    favorite.name = name
    favorite.user = user
    favorite.ref_id = uuid(reference_id)
    favorite.ref_type = reference_type

    return db().add(favorite)
   

@apimethod.auth
def remove(name):
    rs = db().find(auth.Favorite, auth.Favorite.name == name, auth.Favorite.user == user)
    favorite = not_empty(rs.one())

    if favorite.user == user:
        db().remove(favorite)
    else:
        raise TypeError("Not your favorite!")

@apimethod.auth
def resolve(name):
    rs = db().find(auth.Favorite, auth.Favorite.name == name, auth.Favorite.user == user)
    favorite = not_empty(rs.one())
    return unicode(favorite.ref_id)

def valid_name(name):
    valid_chars = "-_.%s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in name if c in valid_chars) 