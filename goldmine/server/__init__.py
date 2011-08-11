#!/usr/bin/env python
#-*- coding:utf-8 -*-

import uuid as _uuid

from goldmine.server.service import Unauthorized
from goldmine.models import *
from goldmine.db import generate_uuid

 
def needauth(func):

    def new(*args, **kwargs):
        if "auth" not in kwargs:
            raise Unauthorized("Authentication token missing")
        
        try:
            u = Token.get_user(kwargs["auth"])
        except Exception, e:
            print e
            raise Unauthorized("Invalid authentication token")
            
        if u is None:
            raise Unauthorized("Invalid authentication token")
            
       
        # keyword arguments are never passed           
        if func.func_code.co_argcount == len(args) + 1 and \
                func.func_code.co_varnames[len(args)] == "user":
            return func(*args, user=u)
        elif func.func_code.co_varnames[len(args)-1] == "user":
            # to avoid username injections
            raise TypeError("%s() takes %d arguments" % (func.func_name, func.func_code.co_argcount-1))
        else:
            return func(*args)

            
    new.rpcenabled = True
    new.needauth = True
    return new

# Resultset to List
def rstolist(rs):
    l = []
    for obj in rs:
        stdobj = obj.__serialize__(nestedness=1)
        l.append(stdobj)
    return l

def noempty(obj):
    if obj is None:
        raise Exception("No such object")
    else:
        return obj
        
def default(val, defaultval):
    if default is None:
        return defaultval
    else:
        return val
        
def uuid(s):
    if s is None:
        return None
    return _uuid.UUID(s)  
    
