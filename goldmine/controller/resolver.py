#!/usr/bin/env python
#-*- coding:utf-8 -*-

import pkgutil
import new

from goldmine import debug
from goldmine.controller import *
from goldmine.utils import singleton

@singleton
class Resolver:


    def __init__(self):
        self.cache = {}
        self.nsmain = __import__(API_NAMESPACE, fromlist=("foo"))
        self.walk(API_NAMESPACE, API_NAMESPACE, self.nsmain)
        
    def walk(self, namespace, mainnamespace, main):
        for importer, package_name, ispkg in pkgutil.iter_modules(main.__path__):
            full_package_name = '%s.%s' % (namespace, package_name)
            module = importer.find_module(package_name).load_module(full_package_name)
            lookup_name = full_package_name[len(mainnamespace)+1:] 
            self.cache[lookup_name] = module
            if ispkg:
                self.walk(full_package_name, mainnamespace, module)
                
    def resolve(self, method, orig_method=None):
        
        if orig_method is None:
            orig_method = method
            
        try:
            if "." in method:
                (ns, method) = method.rsplit(".", 1)
                resolved = getattr(self.cache[ns], method)
            else:
                resolved = getattr(self.nsmain, method)
        except Exception, e:
            debug("Failure resolving call to function '%s'" % (orig_method), module="api_resolve")
            ex = MethodNotFoundException()
            ex.message = "Method not found: %s" % orig_method
            raise ex
            
        return resolved
                
# stupid hack
def get(method, user):
    fn = Resolver().resolve(method)
    if isinstance(fn, apimethod):
        return fn.as_user(user)
    else:
        glob = fn.func_globals.copy()
        glob.update({"user": user})
        return new.function(fn.func_code, glob, argdefs=fn.func_defaults)
