#!/usr/bin/env python
#-*- coding:utf-8 -*-

import pkgutil
import new
import sys
import imp
import os.path

from goldmine import debug, config
from goldmine.controller import *
from goldmine.utils import singleton

""" 
Resolves a function based on string name, 
either from the API_NAMESPACE or from the plugin folder
"""

@singleton
class Resolver:


    def __init__(self):
        self.cache = {}
        self.nsmain = __import__(API_NAMESPACE, fromlist=("foo"))
        self.walk_ns(API_NAMESPACE, API_NAMESPACE, self.nsmain)
        self.walk_plugins(config()["server"]["plugins"], API_NAMESPACE, PLUGIN_PREFIX, True)

        
    def walk_ns(self, namespace, mainnamespace, main):

        """
            Go through namespace of the API, and locate all modules
        """
        for importer, package_name, ispkg in pkgutil.iter_modules(main.__path__):
            full_package_name = '%s.%s' % (namespace, package_name)
            module = importer.find_module(package_name).load_module(full_package_name)
            lookup_name = full_package_name[len(mainnamespace)+1:] 
            self.cache[lookup_name] = module
            if ispkg:
                self.walk_ns(full_package_name, mainnamespace, module)

    def walk_plugins(self, directory, apiprefix, prefix, ispkg=False):

        """
            Go through the plugin directory and locate all modules
            A bit hackish, but it works
        """

        # get all files and directories
        files = os.listdir(directory)

        # storage for modules to load
        modules = []

        # storage for subdirectories to walk
        subdirs = []

        for module in files:
            path = directory + "/" + module

            if os.path.isdir(path):
                subdirs.append((path, prefix + "." + module))

            elif module == "__init__.py":
                ispkg = True
                # load __init__.py first to avoid Runtime errors
                modules.insert(0, ([apiprefix, prefix], path))

            elif module.endswith(".py"):
                modules.append(([apiprefix, prefix, module[:-3]], path))

        for module in modules:

            full_package_name = ".".join(module[0])
            path = module[1]
            
            try:
                resolved_module = imp.load_source(full_package_name, path)
                lookup_name = full_package_name[len(apiprefix)+1:] 
                self.cache[lookup_name] = resolved_module
            except Exception, e:

                if isinstance(e, SyntaxError):
                    debug("Syntax error in '%s' on line %d" % (full_package_name, e.lineno), module="plugin-load")
                else:
                    debug("Exception in '%s' %s" % (full_package_name, repr(e)), module="plugin-load")

                # skip further imports from submodule 
                ispkg = False

        # only walk packages if they contain an __init__.py
        if ispkg:
            for subdir in subdirs:
                self.walk_plugins(subdir[0], apiprefix, subdir[1], ispkg)

                
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
            debug("Failure resolving call to function '%s'" % (orig_method), module="api-resolve")
            ex = MethodNotFoundException()
            ex.message = "Method not found: %s" % orig_method
            raise ex
            
        return resolved



# get function with user context
def get(method, user):
    fn = Resolver().resolve(method)
    if isinstance(fn, apimethod):
        return fn.as_user(user)
    else:
        glob = fn.func_globals.copy()
        glob.update({"user": user})
        return new.function(fn.func_code, glob, argdefs=fn.func_defaults)
