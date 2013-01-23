#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Activity functions
"""
from storm.locals import *

from goldmine import *
from goldmine.db import db
from goldmine.models import *
from goldmine.controller import *

@apimethod.auth
def get(activity_id):
    activity_id = uuid(activity_id, user)
    activity = not_empty(db().get(structure.Activity, activity_id)).serialize()

    # limit access to studies
    studies = []
    for study in activity["studies"]:
        if resolver.get("study.access", user)(study["id"], min_role="read"):
            studies.append(study)

    activity["studies"] = studies
    return activity

@apimethod.auth
def all(project=None):
    rs = db().find(structure.Activity).order_by(structure.Activity.name)
    return rs_to_list(rs)

@apimethod.auth
def search(keyword):

    keyword = "%%%s%%" % keyword
    rs = db().find(structure.Activity, Or(structure.Activity.name.like(keyword), structure.Activity.description.like(keyword)))
    rs = rs.order_by(structure.Activity.name)
    return rs_to_list(rs)

@apimethod.auth("activity.create")
def create(project_id, name, description=None, location={}):
    
    activity = structure.Activity()
    activity.project = db().get(structure.Project, uuid(project_id))
    activity.name = name
    activity.description = description
    
    if len(location):
        loc = structure.Location.from_struct(location)
        activity.location = db().add(loc)
    
    return db().add(activity)

