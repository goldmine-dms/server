#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Project functions
"""
from storm.locals import *

from goldmine import *
from goldmine.db import db
from goldmine.models import *
from goldmine.controller import *

@apimethod.auth
def get(project_id):
    project_id = uuid(project_id, user)
    return not_empty(db().get(structure.Project, project_id))
    
@apimethod.auth
def all():
    rs = db().find(structure.Project).order_by(structure.Project.name)
    return rs_to_list(rs)

@apimethod.auth
def search(keyword):
    keyword = "%%%s%%" % keyword
    rs = db().find(structure.Project, Or(structure.Project.name.like(keyword), structure.Project.description.like(keyword)))
    rs = rs.order_by(structure.Project.name)
    return rs_to_list(rs)
    
@apimethod.auth("project.create")
def create(name, description=None, location={}):
    
    project = structure.Project()
    project.name = name
    project.description = description
    
    if len(location) :
        loc = structure.Location.from_struct(location)
        project.location = db().add(loc)
    
    return db().add(project)
