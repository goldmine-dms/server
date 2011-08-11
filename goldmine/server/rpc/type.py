#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Type functions
"""

from goldmine import *
from goldmine.db import db
from goldmine.models import *

from goldmine.server import needauth, rstolist, noempty, uuid, default
from goldmine.server.service import Unauthorized, rpc

@rpc
def get(tid):
    tid = uuid(tid)
    return noempty(db().get(Type, tid))
    

@rpc
def listing(search):
    if search is None or search == "":
        rs = db().find(Type).order_by(Type.name)
    else:
        rs = db().find(Type, Type.name == search).order_by(Type.name)
    
    return rstolist(rs)

@needauth
def get_extended(tid, user):
    tid = uuid(tid)
    t = noempty(db().get(Type, tid))
    ds = list(t.dataset_xtype)
    ds.extend(list(t.dataset_ytype))
    
    cores = []
    for dataset in ds:
        cores.extend([x.__serialize__(nestedness=1) for x in list(dataset.study.cores)])

    t = t.__serialize__()
    t["datasets"] = [xt.__serialize__(nestedness=1) for xt in ds]
    t["cores"] = cores
    return t

@needauth
def new(name, unit, species, classification, storage, description, user):
    #FIXME: Add authentication
    
    t = Type()
    t.name = name
    t.species = species
    t.classification = default(classification, "main")
    t.storage = default(storage, "float")
    t.unit = unit
    t.description = default(description, "")
    return db().add(t)
