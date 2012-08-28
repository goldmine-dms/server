#!/usr/bin/env python
#-*- coding:utf-8 -*-

from goldmine import *
from goldmine.db import db
from goldmine.models import *
from goldmine.controller import *

@apimethod.auth
def limit(dictionary, keys):
    
    """
    Limit the number of keys exposed by a dictionary
    
    dictionary  = The dictionary to be limited
    keys        = (list) The keys used to limit the dictionary
    """
    
    if isinstance(dictionary, Model):
        dictionary = dictionary.serialize()
    
    limited = {}
    
    try:
        for key in keys:
            limited[key] = dictionary[key]
    except Exception, e:
        raise TypeError("Key not in dictionary: " + e.message)
    
    return limited
