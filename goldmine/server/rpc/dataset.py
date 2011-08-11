#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Dataset functions
"""

import numpy
import datetime

from goldmine import *
from goldmine.db import db, mass_insert
from goldmine.models import *

from goldmine.server import needauth, rstolist, noempty, uuid, default
from goldmine.server.service import Unauthorized
from goldmine.utils import transpose, resample, nantonone

@needauth
def get(dsid, user):
    #FIXME: Add authentication
    dsid = uuid(dsid)
    ds = noempty(db().get(Dataset, dsid))
    
    # Add datapoint counters
    # This is very slow without indexes
    query = "SELECT COUNT(*) FROM measurements WHERE dataset_id = %s"
    result = db().execute(query, (unicode(dsid),));
    num_measurements = result.get_one()[0]
    
    query = "SELECT COUNT(*) FROM datapoints WHERE parameter_id = %s"
    num_datapoints = 0
    for param in ds.params:
        result = db().execute(query, (unicode(param.id),));
        num_datapoints += result.get_one()[0]
    
    ds = ds.__serialize__()
    ds["counters"] = {}
    ds["counters"]["measurements"] = num_measurements
    ds["counters"]["datapoints"] = num_datapoints
    
    ds["metadata"] =_get_metadata(dsid, {"pid": None, "mid": None, "dpid": None})

    return ds
    
    
@needauth
def get_raw(dsid, params, limits, with_ids, user):
    #FIXME: Add authentication
    dsid = uuid(dsid)
    ds = noempty(db().get(Dataset, dsid))    
    
    if limits is None:
        limits = (None, None)

    return transpose(_get_raw_data(ds, params, limits, with_ids))

@needauth
def get_derived(dsid, cfg, user):
    #FIXME: Add authentication
    dsid = uuid(dsid)
    ds = noempty(db().get(Dataset, dsid))        
    return transpose(_get_derived_data(ds, cfg))

@needauth    
def get_metadata(dsid, cfg, user):
    #FIXME: Add authentication
    
    dsid = uuid(dsid)
    ds = noempty(db().get(Dataset, dsid))
    
    return _get_metadata(dsid, cfg)

@needauth
def add_metadata(dsid, pid, mid, dpid, meta, user):
    return _add_metadata(meta, user, uuid(dsid), uuid(pid), uuid(mid), uuid(dpid))

@needauth
def new(study_id, xtype_id, ytype_ids, markertype, markerlocation, description, forked_from, user):
    #FIXME: Add authentication
    study_id = uuid(study_id)
    xtype_id = uuid(xtype_id)

    ds = Dataset()
    ds.study_id = study_id
    ds.xtype_id = xtype_id    
    ds.markertype = default(markertype, "point")
    ds.markerlocation = default(markerlocation, "na")
    ds.description = description
    ds = db().add(ds)
    
    for ytype_id in ytype_ids:
        ytype_id = uuid(ytype_id)     
        ytype = db().get(Type, ytype_id)

        p = Parameter()
        p.ytype = ytype
        db().add(p)
        ds.params.add(p)
        
    if forked_from is not None:
        ds_id_from = uuid(forked_from)
        ds_from = db().get(Dataset, ds_id_from)
        
        lin = Lineage()
        lin.from_dataset = ds_from
        lin.to_dataset = ds
        db().add(lin)
        
    return ds
    
@needauth
def fork(ds_id_from, ds_id_to, user):
    #FIXME: Add authentication
    #FIXME: Check for circular etc
    ds_id_from = uuid(ds_id_from)
    ds_id_to = uuid(ds_id_to)
    
    ds_from = db().get(Dataset, ds_id_from)
    ds_to = db().get(Dataset, ds_id_to)
    
    lin = Lineage()
    lin.from_dataset = ds_from
    lin.to_dataset = ds_to
    return db().add(lin)
    
    
@needauth
def close(ds_id, user):  
    #FIXME: Add authentication
    ds_id = uuid(ds_id)
    ds = noempty(db().get(Dataset, ds_id))
    if ds.closed is None:
        ds.closed = datetime.datetime.now()
    else:
        raise Exception("Dataset already closed")

@needauth
def delete(ds_id, user):
    ds_id = uuid(ds_id)
    ds = noempty(db().get(Dataset, ds_id))
    if ds.closed is not None:
        raise Exception("Dataset is closed and cannot be deleted")
    
    #FIXME: cascade delete, to clean up db
    # metadata, params, measurements, datapoints, lineage
    
    db().remove(ds)

    
    
@needauth
def append(ds_id, measurements, parameters, user):
    #FIXME: Add authentication 
    ds_id = uuid(ds_id)
    #FIXME: Check that parameters.keys() belong to ds
    _append(ds_id, measurements, parameters, user)
    
    
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
    """ Get all datapoints in a dataset, without metadata """

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
    """ Get derived datapoints based on a configuration """

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
