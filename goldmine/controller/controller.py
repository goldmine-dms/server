#!/usr/bin/env python
#-*- coding:utf-8 -*-

from goldmine import debug
from goldmine.controller import *
from goldmine.db import db

class Controller:     
   
    def __init__ (self):
        self.token = None
        self.resolver = Resolver()

    def set_token(self, token):
        self.token = token

    def get_method(self, method):
        resolved = self.resolver.resolve(method)
        try:
            return resolved.token(self.token)
        except MethodNotFoundException, e1:
            raise
        except AttributeError, e2:
            raise MethodNotFoundException()
        except UnauthorizedException, e3:
            debug("Unauthorized call to %s" % (method), module="api-resolve")
            raise
            
    def execute(self, method, *args, **kwargs):    
        debug("%s.%s%s" % (method.__module__, method.__name__, str(args)), module="api-execute")
        return method(*args, **kwargs)

    def on_success(self):
        db().commit()
        
    def on_failure(self):
        db().rollback()

