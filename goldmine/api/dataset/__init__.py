#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Dataset functions
"""

from goldmine import *
from goldmine.db import db
from goldmine.models import *
from goldmine.controller import *

@apimethod.auth
def get(dataset_id):
    #FIXME: User has access?
    dataset_id = uuid(dataset_id)
    ds = not_empty(db().get(dataset.Dataset, dataset_id))
    return ds
    
@apimethod.auth
def fork(from_dataset_id, to_dataset_id):
    #FIXME: User has access?
    #FIXME: Check for circular graph
    from_dataset_id = uuid(from_dataset_id)
    to_dataset_id = uuid(to_dataset_id)
    
    from_dataset = not_empty(db().get(Dataset, from_dataset_id))
    to_dataset = not_empty(db().get(Dataset, to_dataset_id))
    
    return _fork(from_dataset, to_dataset)
    
@apimethod.auth
def close(dataset_id):  
    #FIXME: User has access?
    dataset_id = uuid(dataset_id)
    ds = not_empty(db().get(dataset.Dataset, dataset_id))
    if ds.closed is None:
        ds.closed = datetime.datetime.now()
    else:
        raise Exception("Dataset already closed")
        
@apimethod
def supported_dataset_types():
    names = [obj[0] for obj in dataset.DATASET_TYPES]
    return names

# Private functions

def _fork(from_dataset, to_dataset):
    lineage = Lineage()
    lineage.from_dataset = from_dataset
    lineage.to_dataset = to_dataset
    return db().add(lineage)


def _create(type, study, description, dataset_forked_from=None):
    #FIXME: User has access?
    
    if type not in supported_dataset_types():
        raise Exception("Unsupported type")
        
    ds = dataset.Dataset()
    ds.type = type
    ds.study = study
    ds.description = description
    ds = db().add(ds)
        
    if dataset_forked_from is not None:
        from_dataset_id = uuid(dataset_forked_from)
        from_dataset = not_empty(db().get(dataset.Dataset, from_dataset_id))
        _fork(from_dataset, ds)
                
    return ds
    
    
