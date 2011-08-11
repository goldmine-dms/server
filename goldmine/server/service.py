#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Service implementation, inspired by and reusing concepts from the JSONRPC.org python reference implentation
"""

import sys
import traceback

try:
    import simplejson as json
except ImportError:
    import json

from goldmine.db import db
from goldmine import debug

def rpc(f):
    f.rpcenabled = True
    return f
    
class JSONRPCServiceException(Exception):
    error = -32000
    
class ServerError(JSONRPCServiceException):
    error = -32000
    
class Unauthorized(JSONRPCServiceException):
    error = -31000
        
class ParseError(JSONRPCServiceException):
    error = -32700
    
class InvalidRequest(JSONRPCServiceException):
    error = -32700
    
class MethodNotFound(JSONRPCServiceException):
    error = -32601
    
class InvalidParams(JSONRPCServiceException):
    error = -32602
    
class InternalError(JSONRPCServiceException):
    error = -32603

class JSONRPCService:

    def __init__(self, service=None, auth=None):
        if service == None:
            import __main__ as service
        self.service = service
        self.auth = auth
        self.prefix = [k for k, v in sys.modules.iteritems() if v == self.service][0]

    def handleRequest(self, data):   
        error = None
        id_ = None
        auth = None
        
        
        try:
        
            try:
                req = json.loads(unicode(data))
            except Exception:
                raise ParseError("Parse Error")
            
            try:
                rpcversion = req["jsonrpc"]
                id_ = req["id"]
                method = req["method"]
                params = req["params"]
                if "auth" in req:
                    auth = req["auth"]    
            except Exception:
                raise InvalidRequest("Invalid Request")
                
            if rpcversion != "2.0":
                raise InvalidRequest("Only JSONRPC 2.0 Supported")
            
            try:  
                path = method.rsplit(".", 1)
                if len(path) == 1:
                    method_func = getattr(self.service, path[0])
                else: 
                    module = sys.modules[self.prefix + "." + path[0]]
                    method_func = getattr(module, path[1])
                    
                method_func.rpcenabled # a bit of a hack            
            except Exception:
                raise MethodNotFound("Method Not Found")
                
            try:
                debug("%s%s" % (method, tuple(params)), module="json-rpc")
            
                if auth is not None and hasattr(method_func, "needauth"):
                    result = method_func(*params, auth=auth)
                else:
                    result = method_func(*params)
            except TypeError, e:
                print "== TypeError caught: ", e, " =="
                traceback.print_tb(sys.exc_info()[2])
                raise InvalidParams("Invalid Params: " + e.args[0])
            except Unauthorized:
                raise 
            except Exception, e:
                print "== Exception caught: ", str(type(e)), e, " =="
                traceback.print_tb(sys.exc_info()[2])
                raise ServerError("Internal Server Error: " + e.args[0])
                
            try:
                result = result.__getattribute__("__serialize__")()
            except AttributeError:
                pass
                
            resultdict = {"jsonrpc": "2.0", "result": result, "id": id_}
            
            try:
                resultdata = json.dumps(resultdict)
            except Exception:
                 raise InternalError("Serialization error")  
                 
            # commit the transaction if successful
            db().commit()
           
            return (resultdata, None)
                
        except JSONRPCServiceException, e:
        
            resultdict = {"jsonrpc": "2.0", "error": {"code": e.error, "message": e.args[0]}, "id": id_}
            resultdata = json.dumps(resultdict) 
            
            # rollback any transaction
            db().rollback()
                         
            return (resultdata, e.error)  
            
        except Exception, e:
            print "== Unhandled exception caught: ", str(type(e)), e, " =="
            traceback.print_tb(sys.exc_info()[2])
            
        
            
