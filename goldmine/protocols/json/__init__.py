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

# FIXME: does this belong here?
from goldmine.db import db
from goldmine import controller

    
class JSONRPCProtocol:
    
    content_type = "application/json-rpc"

    def __init__(self, controller):
        self.controller = controller

    def handleRequest(self, data):   
        error = None
        id_ = None
        ctrl = self.controller()
                
        try:
            
            # deserialize
            try:
                req = json.loads(unicode(data))
            except Exception:
                raise JSONRPCParseError("Parse Error")
            
            # gather required parameters
            try:
                version = req["jsonrpc"]
                id_ = req["id"]
                method = req["method"]
                params = req["params"]
                
                if "auth" in req:
                    ctrl.set_token(req["auth"])
                        
            except Exception:
                raise JSONRPCInvalidRequest("Invalid Request")
                
            # check version
            if version != "2.0":
                raise JSONRPCInvalidRequest("Only JSONRPC 2.0 Supported")
            
            # resolve method
            try:
                resolved_method = ctrl.get_method(method)                
            except controller.MethodNotFoundException:
                raise JSONRPCMethodNotFound("Method Not Found")
            
            except controller.UnauthorizedException:                    # pre-run unauthorized
                raise JSONRPCUnauthorized("Unauthorized")
                
            # execute method
            try:
                if isinstance(params, dict):                            # kwargs
                    result = ctrl.execute(resolved_method, **params)
                else:                                                   # args
                    result = ctrl.execute(resolved_method, *params)
            except TypeError, e:
                raise JSONRPCInvalidParams("Invalid Params: " + e.args[0])
            except controller.InvalidRequest, e:
                raise JSONRPCInvalidRequest("Invalid Request: " + e.args[0])
                
            except controller.UnauthorizedException:                    # runtime unauthorized
                raise JSONRPCUnauthorized("Unauthorized") 
                
            except Exception, e:
                print "== Exception caught: ", str(type(e)), e, " =="
                traceback.print_tb(sys.exc_info()[2])
                raise JSONRPCServerError("Internal Server Error: " + e.args[0])
                
            # turn into a serializable structure if returned object supports
            try:
                result = result.__getattribute__("__serialize__")()
            except AttributeError:
                pass
            except Exception, e:
                print "== Exception caught: ", str(type(e)), e, " =="
                traceback.print_tb(sys.exc_info()[2])
                raise JSONRPCServerError("Internal Server Error: " + e.args[0]) 
                
            resultdict = {"jsonrpc": "2.0", "result": result, "id": id_}
            
            # serialize the result
            try:
                resultdata = json.dumps(resultdict)
            except Exception:
                 raise JSONRPCInternalError("Serialization error")  
                 
            # commit the transaction if successful
            ctrl.on_success()
           
            # send it to service layer as a string, 2nd parameter is error code
            return (resultdata, None)
                
        except JSONRPCServiceException, e:
        
            resultdict = {"jsonrpc": "2.0", "error": {"code": e.error, "message": e.args[0]}, "id": id_}
            resultdata = json.dumps(resultdict) 
            
            # rollback any transaction
            ctrl.on_failure()
                         
            return (resultdata, e.error)  
            
        except Exception, e:
            print "== FIXME: Unhandled exception caught in JSONRPC: ", str(type(e)), e, " =="
            traceback.print_tb(sys.exc_info()[2])
            
        
class JSONRPCServiceException(Exception):
    error = -32000
    
class JSONRPCServerError(JSONRPCServiceException):
    error = -32000
    
class JSONRPCUnauthorized(JSONRPCServiceException):
    error = -31000
        
class JSONRPCParseError(JSONRPCServiceException):
    error = -32700
    
class JSONRPCInvalidRequest(JSONRPCServiceException):
    error = -32700
    
class JSONRPCMethodNotFound(JSONRPCServiceException):
    error = -32601
    
class JSONRPCInvalidParams(JSONRPCServiceException):
    error = -32602
    
class JSONRPCInternalError(JSONRPCServiceException):
    error = -32603
           
