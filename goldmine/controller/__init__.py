#!/usr/bin/env python
#-*- coding:utf-8 -*-

import new
import uuid as _uuid

from goldmine.models import auth

exposed_methods = []

API_NAMESPACE = "goldmine.api"
PLUGIN_PREFIX = "plugin"

class MethodNotFoundException(Exception):
    message = "Method not found"

class UnauthorizedException(Exception):
    pass
    
class InvalidRequest(Exception):
    pass

class apimethod:
    
    def __init__(self, method=None, *args, **kwargs):
        self.method = method
        self.auth_required = False
        self.permission = None
        self.argument_types = kwargs
        self.decorator_being_build = False
        self.documentation = ""
        
        if method is None:
            self.decorator_being_build = True
        elif isinstance(method, str):
            self.decorator_being_build = True
            self.permission = [method]
            self.permission.extend(list(args))
        if not self.decorator_being_build:
            self.method_code = self.method.__code__
            self.method.fqn = "%s.%s" % (self.method.__module__, self.method.func_name)
            self._register(self.method)
            
    @staticmethod
    def auth(*args, **kwargs):
        am = apimethod(*args, **kwargs)
        am.auth_required = True
        return am
        
    def as_user(self, user):
        self.check_access(user)
        glob = self.method.func_globals.copy()
        glob.update({"user": user})
        return new.function(self.method_code, glob, argdefs=self.method.func_defaults)
        
    def token(self, token):
        user = auth.Token.get_user(token)
        return self.as_user(user)
        
    def check_access(self, user=None):

        if (self.auth_required or self.permission) and user is None:
            raise UnauthorizedException("Method requires authenticated user")

        if user and user.is_admin():
            return
        
        if self.permission:
            for perm in self.permission:
                if not _get("user.permission.access", user)(unicode(perm)):
                    raise UnauthorizedException("Method requires permission: %s" % perm)

        
    def __call__(self, *args, **kwargs):
    
        if self.decorator_being_build:
            self.method = args[0]
            self.decorator_being_build = False
            self.method_code = self.method.__code__
            self.method.fqn = "%s.%s" % (self.method.__module__, self.method.func_name)
            self._register(self.method)
            return self
        else:
            raise Exception("Need to be called with as object.token(auth_token)(arg0, arg1, ...)")

    def _register(self, method):
        exposed_methods.append(method)
        if method.__doc__:
            self.documentation = method.__doc__
            
            
def rs_to_list(rs, nestedness=1):
    l = []
    for obj in rs:
        stdobj = obj.__serialize__(nestedness=nestedness)
        l.append(stdobj)
    return l

def not_empty(obj):
    if obj is None:
        raise InvalidRequest("No such object")
    else:
        return obj
        
def default(val, defaultval):
    if default is None:
        return defaultval
    else:
        return val
        
def uuid(s, user=None):

    if type(s) == _uuid.UUID:
        return s

    if s is None:
        return None

    if isinstance(s, unicode) and s.startswith("#"):
        
        if user is None:
            raise TypeError("Favorite is not availiable for this request")

        s = s[1:]
        s = _get("favorite.resolve", user)(s)
        
        if not s:
            raise TypeError("Unknown favorite")
            
    try:
        return  _uuid.UUID(s)  
    except:
        raise TypeError("Malformed UUID")
  
# import into namespace
from goldmine.controller.resolver import Resolver, get as _get
from goldmine.controller.controller import Controller
