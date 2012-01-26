#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Study functions
"""

from goldmine import *
from goldmine.db import db
from goldmine.models import *
from goldmine.controller import *

@apimethod.auth
def get(study_id):
    #FIXME: does user have access?
    study_id = uuid(study_id)
    return not_empty(db().get(structure.Study, study_id)) 
    
@apimethod.auth("study.create")
def create(name, description):
    s = structure.Study()
    s.name = name
    s.description = description
    s.owner = user
    return db().add(s)

@apimethod.auth
def list(standalone=False, owned_by_user=False):
    #FIXME: does user have access?
    if standalone:
        subselect = Select(structure.ActivityStudy.study_id, distinct=True)
        if owned_by_user:
            rs = db().find(structure.Study, And(Not(structure.Study.id.is_in(subselect)), structure.Study.owner == user))
        else:
            rs = db().find(structure.Study, Not(structure.Study.id.is_in(subselect)))
    else:
        if owned_by_user:
            rs = db().find(structure.Study, structure.Study.owner == user)
        else:
            rs = db().find(structure.Study)
        
    rs = rs.order_by(structure.Study.name)
    return rs_to_list(rs)
    
@apimethod.auth
def search(keyword):
    #FIXME: does user have access?
    rs = db().find(structure.Study, structure.Study.name == keyword)    #FIXME like search + descr
    return rs_to_list(rs)


#### HERTIL Fix

@apimethod.auth
def lineage(study_id):
    #FIXME: does user have access?


    study_id = uuid(study_id)
    study = noempty(db().get(structure.Study, study_id))

    edges = []
    nodes = []

    for dataset in study.datasets:
        if dataset.parents.count() == 0:
            subtree = _lineage_explore(study, dataset)
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
def add_core(sid, cid):
    # FIXME: Add authentication
    sid = uuid(sid)
    cid = uuid(cid)
    
    study = noempty(db().get(structure.Study, sid))
    activity = noempty(db().get(Activity, cid))    
    activity.studies.add(study)
    
######## PRIVATE STUFF ###############

def _lineage_explore(study, node, parent=None, level=0):

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
        child = _lineage_explore(study, child, node, level + 1)
        if child is not None:
            edges.extend(child[0])
            info.update(child[1])
    
    return (edges, info)





