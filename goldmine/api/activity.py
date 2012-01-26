#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Activity functions

"""
from goldmine import *
from goldmine.db import db
from goldmine.models import *
from goldmine.controller import *

@apimethod.auth(activity_id="uuid")
def get(activity_id):
    
    activity_id = uuid(activity_id)
    return not_empty(db().get(structure.Activity, activity_id)) 

@apimethod.auth
def list():
    rs = db().find(structure.Activity).order_by(structure.Activity.name)
    return rs_to_list(rs)

@apimethod.auth
def search(keyword):
    rs = db().find(structure.Activity, structure.Activity.name == keyword).order_by(structure.Activity.name) #FIXME like search + dscr
    return rs_to_list(rs)

@apimethod.auth("activity.create", project_id="uuid", location="location")
def create(project_id, name, description=None, location={}):
    
    activity = structure.Activity()
    activity.project = db().get(structure.Project, uuid(project_id))
    activity.name = name
    activity.description = description
    
    if len(location) :
        loc = structure.Location.from_struct(location)
        activity.location = db().add(loc)
    
    return db().add(activity)

