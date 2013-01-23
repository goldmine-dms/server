#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import urlparse
import traceback
import pprint

from goldmine import controller
    
class RESTProtocol:
    
    content_type = "application/octet-stream"

    def __init__(self, controller):
        self.controller = controller

    def handleRequest(self, data, env, shortpath):

        error = None
        id_ = None
        ctrl = self.controller()
        
        self.content_type = RESTProtocol.content_type
                        
        try:
        
            query_path = env["PATH_INFO"][len(shortpath)+1:]
            
            # deserialize
            try:
                deserialized = query_path.split("/")
            except Exception:
                raise RESTParseError("Parse Error")
            
            # gather required parameters
            try:
                method = deserialized[0]
                if len(deserialized) > 1:
                    params = deserialized[1:]
                else:
                    params = []
                    
                if "HTTP_COOKIE" in env:
                    jar = urlparse.parse_qs(env["HTTP_COOKIE"])
                    
                    if "auth" in jar:
                        ctrl.set_token(unicode(jar["auth"][0]))
                        
            except Exception:
                raise RESTInvalidRequest("Invalid Request")
            
            # resolve method
            try:
                resolved_method = ctrl.get_method(method)                
            except controller.MethodNotFoundException, e0:
                raise RESTMethodNotFound(e0.message)                        # pre-run not found
            
            except controller.UnauthorizedException, e1:                    # pre-run unauthorized
                raise RESTUnauthorized(e1.message)
                
            # execute method
            try:
                if isinstance(params, dict):                                # kwargs
                    result = ctrl.execute(resolved_method, **params)
                else:                                                       # args
                    result = ctrl.execute(resolved_method, *params)
            except TypeError, e0:
                raise RESTInvalidParams("Invalid Params: " + e0.args[0])
            except controller.InvalidRequest, e1:
                raise RESTInvalidRequest("Invalid Request: " + e1.args[0])
            except controller.MethodNotFoundException, e2:                  # runtime not found
                raise RESTMethodNotFound(e2.message)                
            except controller.UnauthorizedException, e3:                    # runtime unauthorized
                raise RESTUnauthorized(e3.message) 
                
            except Exception, e:
                print "== Exception caught: ", str(type(e)), e, " =="
                traceback.print_tb(sys.exc_info()[2])
                raise RESTServerError("Internal Server Error: " + e.args[0])
                
            # turn into a serializable structure if returned object supports
            try:
                if type(result) not in (str, unicode):
                    try:
                        result = result.serialize()
                    except:
                        pass
                    
                    result = pprint.pformat(result)
                    self.content_type = "text/plain"
                    
            except Exception, e:
               raise RESTInternalError("Serialization error")  
                 
            # commit the transaction if successful
            ctrl.on_success()
           
            # send it to service layer as a string, 2nd parameter is error code
            return (result, 200)
                
        except RESTServiceException, e:
            
            # rollback any transaction
            ctrl.on_failure()
            
            self.content_type = "text/plain"
            return (e.args[0], e.error)  
            
        except Exception, e:
            print "== FIXME: Unhandled exception caught in REST: ", str(type(e)), e, " =="
            traceback.print_tb(sys.exc_info()[2])
            
        
class RESTServiceException(Exception):
    error = 500
    
class RESTServerError(RESTServiceException):
    error = 500
    
class RESTUnauthorized(RESTServiceException):
    error = 401
        
class RESTParseError(RESTServiceException):
    error = 400
    
class RESTInvalidRequest(RESTServiceException):
    error = 400
    
class RESTMethodNotFound(RESTServiceException):
    error = 404
    
class RESTInvalidParams(RESTServiceException):
    error = 406
    
class RESTInternalError(RESTServiceException):
    error = 500
           
