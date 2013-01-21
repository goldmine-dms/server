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
    #FIXME: User has access?
    return sequence_from_dataset(dataset_id)
    
@apimethod.auth("dataset.sequence.create")
def create(study_id, description, index_type_id, index_marker_type="point", index_marker_location="center", dataset_forked_from=None):
    
    study_id = uuid(study_id)
    index_type_id = uuid(index_type_id)
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
    #FIXME: User has access?
    sequence = sequence_from_dataset(dataset_id)
    
    if sequence.dataset.closed:
        raise Exception("Dataset is closed")
    
    type_id = uuid(type_id)
    type = not_empty(db().get(dataset.Type, type_id))
    
    param = dataset.sequence.Parameter()
    param.type = type
    param.sequence = sequence
    param.storage = storage
    param.uncertainty_type = uncertainty_type
    param.uncertainty_value = uncertainty_value
    
    return db().add(param)
    
@apimethod.auth
def add_data(dataset_id, index, parameter_id, value, uncertainty = None, uncertainty_type = "absolute"):
    """
    Add a single measurement, not optimized for mass insert
    
    dataset_id:         UUID = the dataset
    
    index:              number = index location
                        [number, number] = index location, index span
                    
    parameter_id:       UUID = parameter id
                        [UUID, ...]   = ordered list of parameter ids
                                        for corresponding values
                                  
    value:              number = value
                        [number, ...] = ordered list of values 
                                        for corresponding parameter ids
                                    
    uncertainty:        number = uncertainty value
                        [number, ...] = ordered list of uncertainties 
                                        for corresponding parameter ids
                                    
    uncertainty_type:   str = uncertainty type ("absolute" or "relative")
                        [str, ...]    = ordered list of uncertainty types
                                        for corresponding parameter ids
    """
                    
    sequence = sequence_from_dataset(dataset_id)
    
    if sequence.dataset.closed:
        raise Exception("Dataset is closed")
    
    # FIXME user has access?
        
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
        
    if type(parameter_id) in [str, unicode]:
        parameter_id = [parameter_id]
        value = [value]
        uncertainty = [uncertainty]
        uncertainty_type = [uncertainty_type]

    for i, pid in enumerate(parameter_id):
        p = dataset.sequence.Point()
        
        parameter = db().get(dataset.sequence.Parameter, uuid(pid))
        
        if parameter is None:
            raise TypeError("parameter %s is not a valid parameter id" % pid)
        
        if parameter.sequence is not sequence:
            raise TypeError("parameter %s is not a part of current dataset" % pid)
        
        p.parameter = parameter
        p.index = idx
        p.value = value[i]
        
        if uncertainty is not None and uncertainty[i] is not None:
            p.uncertainty_value = uncertainty[i]
            
        if type(uncertainty_type) in [list, tuple]:
            p.uncertainty_type = uncertainty_type[i]
        else:
            p.uncertainty_type = uncertainty_type
            
        db().add(p)
    
    return db().add(idx)

@apimethod.auth
def get_data(dataset_id, parameter_id=None, limit_min=None, limit_max=None):

    """
    dataset_id:         id of the dataset
    
    parameter_id:       not set        - all parameters, in random order
                        UUID           - single parameter
                        [UUID, ...]    - specified parameters in order
                        
    limit_min:          not set        - no lower index limit
                        int, float     - lower index limit specified by number
                        
    limit_max:          not set        - no upper index limit
                        int, float     - upper index limit specified by number
    """

    #FIXME user has access
    
    sequence = sequence_from_dataset(dataset_id)
    
    has_span = sequence.index_marker_type == "span"
        
    if parameter_id is None:
        parameter_id = []
        for parameter in sequence.parameters:
            parameter_id.append(unicode(parameter.id))
            
    elif type(parameter_id) in [str, unicode]:
        parameter_id = [parameter_id]
        
        
    parameter_map = {}
        
    for pid in parameter_id:
        
        parameter = db().get(dataset.sequence.Parameter, uuid(pid))

        if parameter is None:
            raise TypeError("parameter %s is not a valid parameter id" % pid)
        
        if parameter.sequence is not sequence:
            raise TypeError("parameter %s is not a part of current dataset" % pid)
            
        parameter_map[pid] = parameter
        
        
    query = "SELECT \n" + \
            "  dataset_sequence_index.location, %(span)s%(columns)s \n" + \
            "FROM dataset_sequence_index %(joins)s " + \
            "\nWHERE \n" + \
            "  dataset_sequence_index.sequence_id = '%(id)s'\n%(limit)s" + \
            "ORDER BY \n  dataset_sequence_index.location\n"
        
    join = "\nLEFT JOIN dataset_sequence_point as %(rename)s ON \n" + \
           "  %(rename)s.index_id = dataset_sequence_index.id AND \n" + \
           "  %(rename)s.parameter_id = '%(id)s'"
    
    point_column = "\n  %(table)s.value, %(table)s.uncertainty_value, " + \
                   "%(table)s.uncertainty_type"
                   
    point_table = "point_%(index)d"
    
    limit = ""    
    add_columns = []
    add_join = []
    
    if limit_min:
        limit += "AND dataset_sequence_index.location > %f\n" % limit_min
    
    if limit_max:
        limit += "AND dataset_sequence_index.location < %f\n" % limit_max    
            
    for index, parameter in enumerate(parameter_id):
        table_name = point_table % {"index": index}
        add_columns.append(point_column % {"table": table_name})
        add_join.append(join % {"rename": table_name, "id": unicode(parameter)})
        
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
        "columns": len(parameter_id) + 1
    }
    
    for parameter in parameter_id:
        obj["current_parameters"].append(parameter_map[parameter].serialize(1))
        obj["headers"].append(parameter_map[parameter].type.signature())
    
    if has_span:
        obj["span"] = []

    # masks for picking out data from the result
    data_mask = tuple(itertools.chain([0], range(2 if has_span else 1, len(parameter_id)*3, 3)))
    uncertainty_value_mask = range(3 if has_span else 2, len(parameter_id)*3, 3)
    uncertainty_type_mask = range(4 if has_span else 3, len(parameter_id)*3, 3)
    uncertainty_type_table =  {1: "absolute", 2: "relative"}
        
    # populate from result
    for index, row in enumerate(result):
        if has_span:
            obj["span"].append(row[1])
        obj["data"].append([row[i] for i in data_mask])
        obj["uncertainty"].append([row[i] for i in uncertainty_value_mask])
        #obj["uncertainty_type"].append(map(lambda x: x and uncertainty_type_table[x], [row[i] for i in uncertainty_type_mask]))
    
    return obj        
        
    
@apimethod.auth
def add_metadata(dataset_id, parameter_id=None, index_id=None, datapoint_id=None):
    sequence = sequence_from_dataset(dataset_id)
    # FIXME missing implementation
    pass
    
    
# UTIL
def sequence_from_dataset(dataset_id):
    dataset_id = uuid(dataset_id)
    return not_empty(db().find(dataset.sequence.Sequence, dataset.sequence.Sequence.dataset_id == dataset_id).one())

"""
    
@needauth    
def get_metadata(dsid, cfg, user):
    #FIXME: Add authentication
    
    dsid = uuid(dsid)
    ds = noempty(db().get(Dataset, dsid))
    
    return _get_metadata(dsid, cfg)

@needauth
def add_metadata(dsid, pid, mid, dpid, meta, user):
    return _add_metadata(meta, user, uuid(dsid), uuid(pid), uuid(mid), uuid(dpid))


    
    
######################## PRIVATE ###########################################


def _append(ds_id, measurements, parameters, user):

    sql_m_head = "INSERT INTO measurements (id, dataset_id, x, span) VALUES %s"
    sql_m_values = "(%s, %s, %s, %s)"
    m_values = []
    
    sql_p_head = "INSERT INTO datapoints (id, measurement_id, parameter_id, y, quality) VALUES %s"
    sql_p_values = "(%s, %s, %s, %s, %s)" 
    p_values = []

    for p_id in parameters:
        if len(measurements) != len(parameters[p_id]):
            raise TypeError(("The number of measurements (%d) and " +
                            "parameter values (%d, id: %d) must be equal") 
                            % (len(measurements), len(parameters[p_id]), int(p_id)))
      
    ds = db().get(Dataset, ds_id)
      
    for (index, xval) in enumerate(measurements):
    
        xmeta = None
        ymeta = None
        span = None

        #FIXME: Check that this is order with the xtype
        if isinstance(xval, list):
            if len(xval) > 2:
                xmeta = xval[2]
            span = xval[1]
            xval = xval[0]
            
        if xval is None:
            continue
            
        m_id = generate_uuid(True)
        m_values.append((m_id, ds_id, xval, span))
        
        if xmeta is not None:
            # create metadata for m_id
            _add_metadata(xmeta, user,
                          measurement=uuid(m_id),
                          dataset=ds_id)

            

        for p_id in parameters:
            yval = parameters[p_id][index]
            quality = None
            
            if isinstance(yval, list):
                if len(yval) > 2:
                    ymeta = yval[2]
                quality = yval[1]
                yval = yval[0]
                
            if yval is not None:
                dp_id = generate_uuid(True)
                p_values.append((dp_id, m_id, p_id, yval, quality))

                if ymeta is not None:
                    # create metadata for p_id
                    _add_metadata(ymeta, user,
                                  datapoint=uuid(dp_id), 
                                  parameter=uuid(p_id), 
                                  measurement=uuid(m_id), 
                                  dataset=ds_id)


    debug("Inserting %.1e values" % (len(m_values) + len(p_values)), module="dataset-append")

    mass_insert(sql_m_head, sql_m_values, m_values)
    mass_insert(sql_p_head, sql_p_values, p_values)

def _get_raw_data(ds, cols=None, limits=(None,None), with_ids=False):
    "x"" Get all datapoints in a dataset, without metadata "x""

    if cols is None:
        cols = []
        for param in ds.params:
            param_id = unicode(param.id)
            cols.append(param_id)   

    # Build query
    if with_ids:
        leftjoin = "LEFT JOIN datapoints as %s ON " + \
               "%s.measurement_id = measurements.id AND %s.parameter_id = '%s'"
        
        selectquery = "SELECT measurements.x, measurements.id, %s FROM measurements %s " + \
                  "WHERE measurements.dataset_id = '%s' %s" + \
                  "ORDER BY measurements.x"
    else:
        leftjoin = "LEFT JOIN datapoints as %s ON " + \
               "%s.measurement_id = measurements.id AND %s.parameter_id = '%s'"
        
        selectquery = "SELECT measurements.x, %s FROM measurements %s " + \
                  "WHERE measurements.dataset_id = '%s' %s" + \
                  "ORDER BY measurements.x"
    
    lefts = []
    namelist = []
    
    for idx, col in enumerate(cols):
        if with_ids:
            aname = "dp_%d.y, dp_%d.id" % (idx, idx)
        else:
            aname = "dp_%d.y" % idx
        
        name = "dp_%d" % idx

        namelist.append(aname)
        lefts.append(leftjoin % (name, name, name, col))
        
    lefts = " ".join(lefts)
    namelist = ", ".join(namelist)
            
    lim = ""
    if limits[0] is not None:
        lim += "AND measurements.x > %f " % limits[0]
    if limits[1] is not None:
        lim += "AND measurements.x < %f " % limits[1]
            
    query = selectquery % (namelist, lefts, unicode(ds.id), lim)     
    result = db().execute(query)
    return result.get_all()
    
    
def _get_derived_data(ds, cfg):
    "x"" Get derived datapoints based on a configuration "x""

    # set default parameters
    defaults = {"limits": (None, None),
                "params": None,
                "nanthreshold": 0.5,
                "method": "mean_binning",
                "supersample": False}
                
    # merge default config into current config
    for k in defaults:
        if k not in cfg:
            cfg[k] = defaults[k]
    
    data = _get_raw_data(ds, cfg["params"], limits=cfg["limits"])
    
    data = numpy.array(data, dtype=numpy.dtype('float'))
    

    if cfg["method"] == "mean_binning":
        
    
        if "stepsize" in cfg:
            
            rdata = resample.mean_binning(
                                data, stepsize=cfg["stepsize"], 
                                mastermax=cfg["limits"][1], mastermin=cfg["limits"][0], 
                                nanthreshold=cfg["nanthreshold"], supersample=cfg["supersample"]) 
            
        elif "numbins" in cfg:

            rdata = resample.mean_binning(
                                data, numbins=cfg["numbins"], 
                                mastermax=cfg["limits"][1], mastermin=cfg["limits"][0], 
                                nanthreshold=cfg["nanthreshold"], supersample=cfg["supersample"]) 

        else:
            raise TypeError("You must provide either numbins or stepsize")
    else:
        raise NotImplementedError("Method not implemented")
         
    return nantonone(rdata.tolist())
       
def _add_metadata(meta, user, dataset=None, parameter=None, measurement=None, datapoint=None):
    if "annotation" not in meta and "params" not in meta:
        raise TypeError("Invalid Metadata, must contain either annotations or params")
    
    m = Metadata()
    m.dataset_id = dataset
    m.measurement_id = measurement
    m.parameter_id = parameter
    m.datapoint_id = datapoint
    m.creator = user
    
    if "annotation" in meta:
        m.annotation = meta["annotation"]

    db().add(m)

    if "params" in meta and meta["params"] is not None:
        for key in meta["params"]:
            mp = MetadataParams()
            mp.key = key
            mp.value = meta["params"][key]
            db().add(mp)
            m.params.add(mp)

    return m


def _get_metadata(dsid, cfg=None):

    if cfg is None:
        cfg = {}
    
    c = {"pid": False, "mid": False, "dpid": False}
    c.update(cfg)

    for key in c:
        if c[key] is not False:
            c[key] = uuid(c[key])

    args = [Metadata, Metadata.dataset_id == dsid]
    
    if c["pid"] is not False:
        args.append(Metadata.parameter_id == c["pid"])
    if c["mid"] is not False:
        args.append(Metadata.measurement_id == c["mid"])
    if c["dpid"] is not False:
        args.append(Metadata.datapoint_id == c["dpid"])

    metadata = db().find(*args)
    return rstolist(metadata)
"""
