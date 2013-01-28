#!/usr/bin/env python
#-*- coding:utf-8 -*-


"""
Sequence functions
"""

from goldmine import *
from goldmine.db import db
from goldmine.models import *
from goldmine.controller import *

import itertools

@apimethod.auth
def get(dataset_id):
    sequence = sequence_from_dataset(dataset_id, user)
    check_access(user, sequence.dataset.study_id, "read")
    return sequence

@apimethod.auth("dataset.sequence.create")
def create(study_id, description, index_type_id, index_marker_type="point", index_marker_location="center", dataset_forked_from=None):
    
    study_id = uuid(study_id, user)
    check_access(user, study_id, "write")

    index_type_id = uuid(index_type_id, user)
    study = not_empty(db().get(structure.Study, study_id))
    index_type = not_empty(db().get(dataset.Type, index_type_id))


    #FIXME unclean    
    parent = resolver.get("dataset.create", user)(u"sequence", study, description, dataset_forked_from)
        
    sequence = dataset.sequence.Sequence()
    sequence.index_type = index_type
    sequence.index_marker_type = index_marker_type
    sequence.index_marker_location = index_marker_location
    sequence.dataset = parent        
    sequence = db().add(sequence)

    return sequence

@apimethod.auth
def add_parameter(dataset_id, type_id, uncertainty_value=None, uncertainty_type="absolute", storage="float"):

    sequence = sequence_from_dataset(dataset_id, user)
    check_access(user, sequence.dataset.study_id, "write")

    if sequence.dataset.closed:
        raise Exception("Dataset is closed")
    
    type_id = uuid(type_id, user)
    type = not_empty(db().get(dataset.Type, type_id))
    
    param = dataset.sequence.Parameter()
    param.index = len(list(sequence.parameters)) + 1
    param.type = type
    param.sequence = sequence
    param.storage = storage
    param.uncertainty_type = uncertainty_type
    param.uncertainty_value = uncertainty_value
    
    return db().add(param)
    
@apimethod.auth
def add_data(dataset_id, index, parameter_index, value, uncertainty=None):
    """
    Add a single measurement, not optimized for mass insert
    
    dataset_id:         UUID = the dataset
    
    index:              number = index location
                        [number, number] = index location, index span
                    
    parameter_index:    int = parameter index
                        [int, ...]   = ordered list of parameter index
                                        for corresponding values
                                  
    value:              number = value
                        [number, ...] = ordered list of values 
                                        for corresponding parameter ids
                                    
    uncertainty:        number = uncertainty value
                        [number, ...] = ordered list of uncertainties 
                                        for corresponding parameter ids
                                    
    """
                    
    sequence = sequence_from_dataset(dataset_id, user)
    check_access(user, sequence.dataset.study_id, "write")

    if sequence.dataset.closed:
        raise Exception("Dataset is closed")
            
    if type(index) in [tuple, list]:
        
        if sequence.index_marker_type != "span":
            raise TypeError("dataset cannot contain spanned points")
            
        if len(index) != 2:
            raise TypeError("index list must be two elements [index, span]")
        
        span = index[1]
        index = index[0]
                
    else:
        
        if index is None:
            raise TypeError("index location must be a number")

        span = None
        
    idx = dataset.sequence.Index()
    idx.location = index
    idx.span = span
    idx.sequence = sequence
        
    if type(parameter_index) is int:
        parameter_index = [parameter_index]
        value = [value]
        uncertainty = [uncertainty]

    for i, pi in enumerate(parameter_index):
        p = dataset.sequence.Point()
        
        p.parameter_index = pi
        p.index = idx
        p.value = value[i]
        
        if uncertainty is not None and uncertainty[i] is not None:
            p.uncertainty_value = uncertainty[i]
            
        db().add(p)
    
    return db().add(idx)

@apimethod.auth
def get_data(dataset_id, parameter_index=None, limit_min=None, limit_max=None):

    """
    dataset_id:         id of the dataset
    
    parameter_index:    not set        - all parameters
                        int           -  single parameter
                        [int, ...]    - specified parameters in order
                        
    limit_min:          not set        - no lower index limit
                        int, float     - lower index limit specified by number
                        
    limit_max:          not set        - no upper index limit
                        int, float     - upper index limit specified by number
    """
    
    sequence = sequence_from_dataset(dataset_id, user)
    check_access(user, sequence.dataset.study_id, "read")

    has_span = sequence.index_marker_type == "span"
        
    if parameter_index is None:
        parameter_index = []
        for parameter in sequence.parameters:
            parameter_index.append(parameter.index)
            
    elif type(parameter_index) is int:
        parameter_index = [parameter_index]
            
    parameter_map = {}
        
    for pid in parameter_index:
        
        parameter = db().find(dataset.sequence.Parameter, 
                dataset.sequence.Parameter.index == pid, 
                dataset.sequence.Parameter.sequence == sequence).one()

        if parameter is None:
            raise TypeError("Parameter index was not found in dataset")
            
        parameter_map[pid] = parameter
        
        
    query = "SELECT \n" + \
            "  dataset_sequence_index.location, %(span)s%(columns)s \n" + \
            "FROM dataset_sequence_index %(joins)s " + \
            "\nWHERE \n" + \
            "  dataset_sequence_index.sequence_id = '%(id)s'\n%(limit)s" + \
            "ORDER BY \n  dataset_sequence_index.location\n"
        
    join = "\nLEFT JOIN dataset_sequence_point as %(rename)s ON \n" + \
           "  %(rename)s.index_id = dataset_sequence_index.id AND \n" + \
           "  %(rename)s.parameter_index = %(index)s"
    
    point_column = "\n  %(table)s.value, %(table)s.uncertainty_value"                   
    point_table = "point_%(index)d"
    
    limit = ""    
    add_columns = []
    add_join = []
    
    if limit_min:
        limit += "AND dataset_sequence_index.location > %f\n" % limit_min
    
    if limit_max:
        limit += "AND dataset_sequence_index.location < %f\n" % limit_max    
            
    for index, parameter in enumerate(parameter_index):
        table_name = point_table % {"index": index}
        add_columns.append(point_column % {"table": table_name})
        add_join.append(join % {"rename": table_name, "index": parameter})
        
    add_columns = ", ".join(add_columns)
    add_join = " ".join(add_join)
    
    query = query % {
        "span": "dataset_sequence_index.span, " if has_span else "",
        "columns": add_columns, 
        "joins": add_join,
        "id": sequence.id,
        "limit": limit
    }
            
    result = db().execute(query).get_all()
    
    obj = {
        "current_parameters": [],
        "headers": [sequence.index_type.signature()],
        "data": [],
        "uncertainty": [],
        "sequence": sequence.serialize(),
        "rows": len(result),
        "columns": len(parameter_index) + 1
    }
    
    for parameter in parameter_index:
        obj["current_parameters"].append(parameter_map[parameter].serialize(1))
        obj["headers"].append(parameter_map[parameter].type.signature())
    
    if has_span:
        obj["span"] = []

    # masks for picking out data mapped to the SQL command
    # data at parameter columns
    n = 1 if has_span else 0
    data_mask = range(n+1, (len(parameter_index)+n)*2, 2)

    # data at index column
    data_mask.insert(0, 0)
    
    # populate from result
    # FIXME looks slow, consider moving to numpy
    debug("(dataset.sequence.get_data) Enter list populate", module="fixme")
    for row in result:
        if has_span:
            obj["span"].append(row[1])
        obj["data"].append([row[i] for i in data_mask])
        obj["uncertainty"].append([row[i+1] for i in data_mask[1:]])
    debug("(dataset.sequence.get_data) Exit list populate", module="fixme")


    return obj        
        

@apimethod.auth
def add_metadata(dataset_id, parameter_index=None, index_id=None, datapoint_id=None):
    sequence = sequence_from_dataset(dataset_id, user)
    check_access(user, sequence.dataset.study_id, "write")

    # FIXME missing implementation
    pass
    
#@apimethod.internal
def purge(dataset_id):
    sequence = sequence_from_dataset(dataset_id, user)
    for i, index in enumerate(sequence.indicies):

        for point in index.points:
            db().remove(point)

        db().remove(index)

        if i % 1000 == 0 and i > 0:
            debug("Purged %d datapoints, committing" % i, module="dataset-sequence-purge")
            db().commit()

    for param in sequence.parameters:
        db().remove(param)

    db().remove(sequence)
    


# UTIL
def sequence_from_dataset(dataset_id, user):
    dataset_id = uuid(dataset_id, user)
    return not_empty(db().find(dataset.sequence.Sequence, dataset.sequence.Sequence.dataset_id == dataset_id).one())


def check_access(user, study_id, role, throw=True):
    if not resolver.get("study.access", user)(study_id, min_role=role):
        if throw: raise UnauthorizedException("You are not authorized to view this sequence")
        return False
    return True
