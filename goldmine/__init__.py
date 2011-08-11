#!/usr/bin/env python
#-*- coding:utf-8 -*-

import time
import os.path
import sys

from termcolor import colored
from configobj import ConfigObj

from goldmine.utils import singleton

class ConfigurationError(Exception):
    pass

@singleton
class config(dict):

    def __init__(self, filename, customized={}):
    
        if not os.path.exists(filename):
            raise ConfigurationError("Configuration file does not exist")
        try:
            cfg = ConfigObj(filename)
        except Exception, e:
            raise ConfigurationError("Configuration file has a syntax error")
            
            
        for c in customized:
            cfg[c] = customized[c]

        dict.__init__(self, cfg)
        
        if "debug" in self:
            self.debug = (self["debug"] == "true")
            del self["debug"]
        else:
            self.debug = False
        

def debug(message, line=None, params=None, module=None, always=False):
    c = config()
    
    message = str(message)
    
    message = message.replace("\r", "")
    message = message.replace("\n", "\\n ")
    
    if len(message) > 100:
        message = message[0:100] + "..."
        
    
    if (c.debug and module not in c["debug_exclude"] or always):
    
        if module:
            print colored("<%s>" % module, 'blue'),
            
        if line:
            print colored("[%03d]" % line, 'white'),
        
        print colored(message,'yellow'),
        
        if params:
            print colored(params, 'red')
        else:
            print
            
        sys.stdout.flush()

            
NaN = float('nan')
