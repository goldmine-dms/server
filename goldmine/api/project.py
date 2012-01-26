#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Project functions
"""

from goldmine import *
from goldmine.db import db
from goldmine.models import *
from goldmine.controller import *

@apimethod.auth
def get(project_id):
    project_id = uuid(project_id)
        
    return not_empty(db().get(structure.Project, project_id))
    
@apimethod.auth
def list():
    rs = db().find(structure.Project).order_by(structure.Project.name)
    return rs_to_list(rs)

@apimethod.auth
def search(keyword):
    rs = db().find(structure.Project, structure.Project.name == keyword).order_by(structure.Project.name)
    return rs_to_list(rs)
    
@apimethod.auth("project.create", location="location")
def create(name, description=None, location={}):
    
    project = structure.Project()
    project.name = name
    project.description = description
    
    if len(location) :
        loc = structure.Location.from_struct(location)
        project.location = db().add(loc)
    
    return db().add(project)
