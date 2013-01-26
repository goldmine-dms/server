#!/usr/bin/env python
#-*- coding:utf-8 -*-


"""
Dataset.Type functions
"""
from storm.locals import *

from goldmine import *
from goldmine.db import db
from goldmine.models import *
from goldmine.controller import *


@apimethod.auth
def get(type_id):
    type_id = uuid(type_id, user)
    return not_empty(db().get(dataset.Type, type_id))


@apimethod.auth("dataset.type.create")
def create(name, unit, description=None, uniname=None): 

    rs = db().find(dataset.Type, dataset.Type.name == name)

    if not rs.is_empty():
        raise TypeError("Type already exists") 

    type = dataset.Type()
    type.name = name
    type.unit = unit
    type.description = description
    type.uniname = uniname
    return db().add(type)

@apimethod
def all():
    rs = db().find(dataset.Type).order_by(dataset.Type.name)
    return rs_to_list(rs)
    
@apimethod
def search(keyword):
    keyword = "%%%s%%" % keyword
    rs = db().find(dataset.Type, Or(dataset.Type.name.like(keyword), dataset.Type.description.like(keyword)))
    rs = rs.order_by(dataset.Type.name)
    return rs_to_list(rs)