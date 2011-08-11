#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Admin functions
"""

import re

from goldmine import *
from goldmine.db import db
from goldmine.models import *

from goldmine.server import needauth
from goldmine.server.service import Unauthorized
from goldmine.utils import debugger

    
@needauth
def restart(user):
    """ 
    ADMIN: Restart the server
    FIXME: Only works with CherryPy
    """
    if not user.is_admin():
        raise Unauthorized("Unauthorized")  
          
    import sys, os, signal, time
    python = sys.executable
    os.execl(python, python, * sys.argv)

@needauth
def sqlquery(query, user):
    """ ADMIN: Preform a raw SQL query """
    if not user.is_admin():
        raise Unauthorized("Unauthorized")  
     
    pattern_comment = re.compile('(--.*\n)') # remove comments
    pattern_split = re.compile(';\s*')    # split on ;<whitespace>
    
    query = pattern_comment.sub("\n\n", query);
     
    conn = db()
    
    for query in pattern_split.split(query):
        query = query.strip();
        if len(query) > 0:
            debug(query, module = "raw-query")
            
            o = conn.execute(query)           

@needauth
def dbg(user):
    """ ADMIN: Drop into a debugger """
    
    if not user.is_admin():
        raise Unauthorized("Unauthorized")

    print "++++ Debugger requested by", user.username, "++++"
    debugger()
