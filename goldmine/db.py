#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
goldmine.db
"""

import time
import threading
import math
import uuid as _uuid

from random import getrandbits

from storm.locals import Store, create_database, UUID

from goldmine import *
from goldmine.utils import singleton, group

def generate_uuid(as_string=False):
    # as string is about 17 times faster than creating an UUID object
    # FIXME: generate valid UUID4s - not entirely random
    # FIXME: switch to UUID1?
    if as_string:
        x = hex(getrandbits(128))[2:-1].rjust(32, "0")
        return x[:8]  + "-" + x[8:12] + "-" + x[12:16] + "-" + x[16:20] + "-" + x[20:]
    else:
        return _uuid.uuid4()

def mass_insert(shead, svalues, values):

    PART = 1000 # page size

    debug("Inserting %d groups" % math.ceil(len(values)/float(PART)), module="mass-insert")
    
    # Paginate for to minimize memory usage (groups is a generator)
    groups = group(values, PART)

    start = time.time()

    for g in groups:
        v = []       
        for val in g:
            if val is not None:
                # Convert to SQL syntax
                val = ['NULL' if x is None else "'%s'" % str(x) for x in val]
                v.append(svalues % tuple(val))
        s = ",".join(v)
        del v
        s = shead % s
        db().execute(s, noresult=True)
    
    end = time.time()    
    debug("Done, %.1f INSERT pr. second" % (len(values)/(end-start)), module="mass-insert")

@singleton
class Database:

    def __init__(self):        
        self.cursorcount = 0
        self.database = create_database(config()["database"]["connection"])
        self.stores = {}
        
    def store(self):
            
        t = threading.current_thread().ident
        if t not in self.stores:
            debug("Spawning DB connection for %s" % str(t), module="database")
            self.stores[t] = Store(self.database)  
        return self.stores[t] 
        
        
db = Database().store
