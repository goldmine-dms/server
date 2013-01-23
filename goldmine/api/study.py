#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Study functions 
"""

from storm.locals import *

from goldmine import *
from goldmine.db import db
from goldmine.models import *
from goldmine.controller import *


@apimethod.auth
def get(study_id):

    check_access(user, study_id, "read")

    study_id = uuid(study_id, user)
    return not_empty(db().get(structure.Study, study_id)) 
    
@apimethod.auth("study.create")
def create(name, description=None):
    s = structure.Study()
    s.name = name
    s.description = description
    s.owner = user
    return db().add(s)

@apimethod.auth
def all(owned_by_user=False):

    if owned_by_user:
        # owned == access
        rs = db().find(structure.Study, structure.Study.owner == user)
        rs = rs.order_by(structure.Study.name)
        return rs_to_list(rs)

    else:
        rs = db().find(structure.Study)
        rs = rs.order_by(structure.Study.name)
        result = []
        for study in rs:
            if check_access(user, study.id, "read", throw=False):
                result.append(study)
        return rs_to_list(result)
        
    
@apimethod.auth
def search(keyword):
    keyword = "%%%s%%" % keyword
    rs = db().find(structure.Study, Or(structure.Study.name.like(keyword), structure.Study.description.like(keyword)))   
    result = []
    for study in rs:
        if check_access(user, study.id, "read", throw=False):
            result.append(study)
    return rs_to_list(result)

@apimethod.auth
def lineage(study_id):

    check_access(user, study_id, "read")

    study_id = uuid(study_id, user)
    study = not_empty(db().get(structure.Study, study_id))

    edges = []
    nodes = []

    for dataset in study.datasets:
        if dataset.parents.count() == 0:
            subtree = generate_lineage_tree(study, dataset)
            if subtree is not None:
                edges.extend(subtree[0])
                nodes.append(subtree[1])
   
    nodedict = {}
    for idx, node in enumerate(nodes):
        for obj in node:
            if obj not in nodedict:
                nodedict[obj] = node[obj]
            elif node[obj]["level"] > nodedict[obj]["level"]:
                nodedict[obj]["level"] = node[obj]

    return {"edges": list(set(edges)), "nodes": nodedict}

@apimethod.auth
def add_activity(study_id, activity_id):
    
    check_access(user, study_id, "admin")

    study_id = uuid(study_id, user)
    activity_id = uuid(activity_id, user)
    
    study = not_empty(db().get(structure.Study, study_id))
    activity = not_empty(db().get(structure.Activity, activity_id))    
    activity.studies.add(study)
    

@apimethod.auth
def add_group(study_id, group_id, role):
    """
        Give group access to study
    """

    check_access(user, study_id, "admin")

    study_id = uuid(study_id, user)
    group_id = uuid(group_id, user)

    # FIXME: check that ids are present in referenced sets
    sg = auth.StudyGroup()
    sg.study_id = study_id
    sg.group_id = group_id
    sg.role = role

    return db().add(sg)

@apimethod.auth
def remove_group(study_id, group_id):
    """
        Remove group access to study
    """

    check_access(user, study_id, "admin")

    study_id = uuid(study_id, user)
    group_id = uuid(group_id, user)

    rs = db().find(auth.StudyGroup, auth.StudyGroup.study_id == study_id, auth.StudyGroup.group_id == group_id).one()

    if rs:
        db().remove(rs)
    else:
        raise TypeError("Group access not found")

@apimethod.auth
def access(study_id, user_id=None, min_role="read"):
    """
        Checks if user has access to study

        study_id:   the study to check
        user_id:    the user to check
                    None for current user
        min_role:   the minimal role requested
    """

    #FIXME investigate caching

    study_id = uuid(study_id, user)
    user_id = uuid(user_id, user)
 
    try:
        min_role = auth.StudyGroup.ROLEMAP[min_role]
    except KeyError:
        raise TypeError("Invalid role '%s'" % min_role)

    if user_id is None:
        user_id = user.id

    the_user = not_empty(db().get(auth.User, user_id))

    if the_user.is_admin():
        return True

    study = not_empty(db().get(structure.Study, study_id))

    if the_user == study.owner:
        return True

    checker = resolver.get("group.has_member", user)

    for sg in study.access:
        if sg.ROLEMAP[sg.role] >= min_role:         # requested role available in group
            if checker(sg.group_id, user_id):       # check for user is member of group
                return True
    return False

######## PRIVATE STUFF ###############

def generate_lineage_tree(study, node, parent=None, level=0):

    if node.study is not study:
        return None

    edges = []
    info = {}
    info[unicode(node.id)] = {"description": node.description, "level": level}    
    parents = list(node.parents)
    
    try:
        parents.remove(parent)
    except:
        pass

    if len(parents) > 0:
        for p in parents:
            info[unicode(p.id)] = {"description": p.description,
                                   "level": level-1}
                                   
    for child in node.children:
        edges.append((unicode(node.id), unicode(child.id)))
        child = generate_lineage_tree(study, child, node, level + 1)
        if child is not None:
            edges.extend(child[0])
            info.update(child[1])
    
    return (edges, info)


def check_access(user, study_id, role, throw=True):
    if not resolver.get("study.access", user)(study_id, min_role=role):
        if throw: raise UnauthorizedException("You are not authorized to view this study")
        return False
    return True