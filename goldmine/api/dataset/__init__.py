#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Dataset functions
"""

import datetime

from goldmine import *
from goldmine.db import db
from goldmine.models import *
from goldmine.controller import *

@apimethod.auth
def get(dataset_id):
    dataset_id = uuid(dataset_id, user)
    ds = not_empty(db().get(dataset.Dataset, dataset_id))
    check_access(user, ds.study_id, "read")
    return ds
    
@apimethod.auth
def fork(from_dataset_id, to_dataset_id, fork_type="derived"):
    #FIXME: Check for circular graph
    from_dataset_id = uuid(from_dataset_id, user)
    to_dataset_id = uuid(to_dataset_id, user)
    
    from_dataset = not_empty(db().get(Dataset, from_dataset_id))
    to_dataset = not_empty(db().get(Dataset, to_dataset_id))
    
    check_access(user, from_dataset.study_id, "read")
    check_access(user, to_dataset.study_id, "write")

    # FIXME: pass on to private function, what happens to user?
    return do_fork(from_dataset, to_dataset, user)
    
@apimethod.auth("dataset.close")
def close(dataset_id):

    # Fixme: only owner should be able to close

    dataset_id = uuid(dataset_id, user)
    ds = not_empty(db().get(dataset.Dataset, dataset_id))

    check_access(user, ds.study_id, "write")

    if ds.closed is None:
        ds.closed = datetime.datetime.now()
    else:
        raise Exception("Dataset already closed")

@apimethod.auth("dataset.purge")
def purge(dataset_id):  

    # Fixme: only owner should be able to purge?

    dataset_id = uuid(dataset_id, user)
    ds = not_empty(db().get(dataset.Dataset, dataset_id))

    check_access(user, ds.study_id, "write")


    if ds.closed is None:
        db().remove(ds)
        #FIXME: cascade
    else:
        raise Exception("Cannot delete closed datasets")
        
        
@apimethod
def supported_dataset_types():
    names = [obj[0] for obj in dataset.DATASET_TYPES]
    return names

# Private functions

def do_fork(from_dataset, to_dataset, user, fork_type="derived"):
    #FIXME user wierdness
    lineage = structure.Lineage()
    lineage.from_dataset = from_dataset
    lineage.to_dataset = to_dataset
    lineage.forked_by = user
    lineage.fork_type = fork_type
    return db().add(lineage)

def create(type, study, description, dataset_forked_from=None, fork_type="derived"):

    check_access(user, study.id, "write")
    
    supported = resolver.get("dataset.supported_dataset_types", user)()
    if type not in supported:
        raise Exception("Unsupported type")
        
    ds = dataset.Dataset()
    ds.type = type
    ds.creator = user
    ds.study = study
    ds.description = description
    ds = db().add(ds)
        
    if dataset_forked_from is not None:
        from_dataset_id = uuid(dataset_forked_from, user)
        from_dataset = not_empty(db().get(dataset.Dataset, from_dataset_id))
        #FIXME
        do_fork(from_dataset, ds, user, fork_type)
                
    return ds
    
    
def check_access(user, study_id, role, throw=True):
    if not resolver.get("study.access", user)(study_id, min_role=role):
        if throw: raise UnauthorizedException("You are not authorized to view this dataset")
        return False
    return True