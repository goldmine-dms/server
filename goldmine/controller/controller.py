#!/usr/bin/env python
#-*- coding:utf-8 -*-

from goldmine.controller import Resolver
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
            print e
            raise UnauthorizedException()
            
    def execute(self, method, *args, **kwargs):
        return method(*args, **kwargs)

    def on_success(self):
        db().commit()
        
    def on_failure(self):
        db().rollback()

