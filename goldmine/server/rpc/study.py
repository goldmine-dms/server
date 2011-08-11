#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Study functions
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

    return noempty(db().get(Study, sid)) 
    
@needauth
def new(name, description, user):
    # FIXME: Add authentication
    s = Study()
    s.name = name
    s.description = description
    s.owner = user
    return db().add(s)


@needauth
def listing(search, standalone, user):
    #FIXME: Add authentication
    if standalone:
        subselect = Select(CoreStudy.study_id, distinct=True)
        if search is None or search == "":
            rs = db().find(Study, Not(Study.id.is_in(subselect)))
        else:
            rs = db().find(Study, Not(Study.id.is_in(subselect)), Study.name == search)
    else:
        if search is None or search == "":
            rs = db().find(Study)
        else:
            rs = db().find(Study, Study.name == search)

    rs = rs.order_by(Study.name)
    return rstolist(rs)

@needauth
def my(user):
    rs = db().find(Study, Study.owner == user).order_by(Study.name)
    return rstolist(rs)

@needauth
def lineage(sid, user):
    #FIXME: Add authentication

    sid = uuid(sid)
    study = noempty(db().get(Study, sid))

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

@needauth
def add_core(sid, cid, user):
    # FIXME: Add authentication
    sid = uuid(sid)
    cid = uuid(cid)
    
    study = noempty(db().get(Study, sid))
    core = noempty(db().get(Core, cid))    
    core.studies.add(study)
    
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





