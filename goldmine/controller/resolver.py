#!/usr/bin/env python
#-*- coding:utf-8 -*-

import pkgutil

from goldmine import debug
from goldmine.controller import *
from goldmine.utils import singleton

@singleton
class Resolver:
    namespace = "goldmine.api"

    def __init__(self):
        self.cache = {}
        self.nsmain = __import__(self.namespace, fromlist=("foo"))
        self.walk(self.namespace, self.namespace, self.nsmain)
        
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
            raise MethodNotFoundException()
            
        return resolved
                
   
