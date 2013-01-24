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
from goldmine import controller

    
class JSONRPCProtocol:
    
    content_type = "application/json-rpc"

    def __init__(self, controller):
        controller()
        self.controller = controller

    def handleRequest(self, data, env, shortpath):
        error = None
        id_ = None
        ctrl = self.controller()
        
        if env["REQUEST_METHOD"] != "POST":
            self.content_type = "text/html"
            return ("Invalid request: Only POST queries allowed.", 400) 
        else:
            self.content_type = JSONRPCProtocol.content_type
            
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
            except controller.MethodNotFoundException, e0:
                raise JSONRPCMethodNotFound(e0.message)                  # pre-run not found
            except controller.UnauthorizedException, e1:                 # pre-run unauthorized
                raise JSONRPCUnauthorized(e1.message)
                
            # execute method
            try:
                if isinstance(params, dict):                            # kwargs
                    result = ctrl.execute(resolved_method, **params)
                else:                                                   # args
                    result = ctrl.execute(resolved_method, *params)
            except TypeError, e0:
                raise JSONRPCInvalidParams("Invalid Params: " + e0.args[0])
            except controller.InvalidRequest, e1:
                raise JSONRPCInvalidRequest("Invalid Request: " + e1.args[0])
            except controller.MethodNotFoundException, e2:                  # runtime not found
                raise JSONRPCMethodNotFound(e2.message)                
            except controller.UnauthorizedException, e3:                    # runtime unauthorized
                raise JSONRPCUnauthorized(e3.message) 
                
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
            try:
                ctrl.on_success()
            except Exception, e:
                raise JSONRPCInternalError("Commit failed: " + repr(e))

            # send it to service layer as a string, 2nd parameter is error code
            return (resultdata, 200)
                
        except JSONRPCServiceException, e:
        
            resultdict = {"jsonrpc": "2.0", "error": {"code": e.error, "message": e.args[0]}, "id": id_}
            resultdata = json.dumps(resultdict) 
            
            # rollback any transaction
            ctrl.on_failure()
                         
            return (resultdata, 200)  
            
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
           
