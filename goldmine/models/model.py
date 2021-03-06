#!/usr/bin/env python
#-*- coding:utf-8 -*-

# 
# Storm Serializable Model
# 

import uuid
import datetime
import pprint

import storm.references
from storm.locals import *

from goldmine import debug, config

class SerializationError(Exception):
    pass
    

class Model(Storm):

    __export__ = []
    
    __serialize_direct_types__ = [int, float, long, str, unicode, bool, type(None)]
    __serialize_str_types__   =  [uuid.UUID, datetime.datetime]
    __serialize_list_types__   = [tuple, list]
    __serialize_dict_types__   = [dict]
    
    
    def __storm_loaded__(self):
        if config().debug and "storm-load" not in config()["debug_exclude"]:
            debug(self.__class__.__name__, module = "storm-load", params = "\n" + pprint.pformat(self.__serialize__()))
   
    def __storm_flushed__(self):
        if config().debug and "storm-save" not in config()["debug_exclude"]:
            debug(self.__class__.__name__, module = "storm-save", params = "\n" + pprint.pformat(self.__serialize__()))

    def serialize(self, nestedness = 0):
        return self.__serialize__(nestedness)
    
    def __serialize__(self, nestedness = 0):
           
        obj = {}
        
        for name in self.__export__:
            if isinstance(name, tuple):
                if nestedness > 0:
                    name = name[1]
                else:
                    name = name[0]
            
            if isinstance(name, str):
                attr = self.__getattribute__(name)    
                obj[name] = self.__serialize_inner__(attr, nestedness)
                    
        return obj

        
    def __serialize_inner__(self, attr, nestedness = 0):
            
        if isinstance(attr, storm.references.BoundReferenceSet) or isinstance(attr, storm.references.BoundIndirectReferenceSet):
            attrlist = []
            for el in attr:
                attrlist.append(el)
            attr = attrlist
            
        for dt in self.__serialize_direct_types__:
            if isinstance(attr, dt):
                return attr                
                
        for dt in self.__serialize_str_types__:
            if isinstance(attr, dt):
                return unicode(attr)  
                
        for lt in self.__serialize_list_types__:
            if isinstance(attr, lt):
                obj = []
                for el in attr:
                    obj.append(self.__serialize_inner__(el, nestedness + 1))
                return obj

        for dt in self.__serialize_dict_types__:
            if isinstance(attr, dt):
                obj = {}
                for el in attr.keys():
                    print "hey", el
                    obj[el] = self.__serialize_inner__(attr[el], nestedness + 1)
                return obj
                
        try:
            return attr.__getattribute__("__serialize__")(nestedness + 1)
        except AttributeError:
            raise SerializationError("Cannot serialize %s in level %d" % (str(attr), nestedness))
