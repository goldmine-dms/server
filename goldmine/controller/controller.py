#!/usr/bin/env python
#-*- coding:utf-8 -*-

from goldmine import debug
from goldmine.controller import Resolver, UnauthorizedException
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
        except Exception, e:
            debug("Unauthorized call to %s" % (method), module="api_resolve")
            raise UnauthorizedException()
            
    def execute(self, method, *args, **kwargs):
        debug("%s%s" % (method.func_name, str(args)), module="api_execute")
        return method(*args, **kwargs)

    def on_success(self):
        db().commit()
        
    def on_failure(self):
        db().rollback()

