#!/usr/bin/env python
#-*- coding:utf-8 -*-

import code
import sys
import math
import time

from itertools import islice, chain

def singleton(cls):
    """@singleton, turns the given class into a singleton
    From: http://www.python.org/dev/peps/pep-0318/
    """
    instances = {}
    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getinstance
    
def transpose(lists):
    """ transposing a list

    From: http://code.activestate.com/recipes/410687-transposing-a-list-of-lists-with-different-lengths/
    """
    if not lists: return []
    return map(lambda *row: list(row), *lists)
    
    
def retry(ExceptionToCheck, tries=3, delay=0.5, backoff=2):
    """Retry decorator
    original from http://wiki.python.org/moin/PythonDecoratorLibrary#Retry
    """
    def deco_retry(f):
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 0:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck, e:
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
                    lastException = e
            raise lastException
        return f_retry # true decorator
    return deco_retry

def debugger():
    """ Drop into debugger
        
    From: http://effbot.org/librarybook/code.htm
    """


    # use exception trick to pick up the current frame
    try:
        raise None
    except:
        frame = sys.exc_info()[2].tb_frame.f_back

    # evaluate commands in current namespace
    namespace = frame.f_globals.copy()
    namespace.update(frame.f_locals)

    code.interact(banner="*** DEBUGGER ENTER ***", local=namespace)
    print "*** DEBUGGER EXIT ***"

    
def group(iterable, size):
    """ Group an interable into a n-tuples iterable (generator)
    
    From: http://code.activestate.com/recipes/303279/
    """
    sourceiter = iter(iterable)
    while True:
        batchiter = islice(sourceiter, size)
        yield chain([batchiter.next()], batchiter)
        
        
def nantonone(obj):
    """ Convert nans to none in lists and nested lists """
    def nested(inner):
        if isinstance(inner, list):
            return nantonone(inner)
        if math.isnan(inner):
            inner = None
        return inner
        
    return map(nested, obj)
    
    
    
    
    
    
