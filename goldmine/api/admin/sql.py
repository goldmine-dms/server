#!/usr/bin/env python
#-*- coding:utf-8 -*-

import re

from goldmine import *
from goldmine.db import db
from goldmine.controller import *

@apimethod.auth("admin.sql.query")
def query(query):
    """ Preform a raw SQL query """
     
    pattern_comment = re.compile('(--.*\n)') # remove comments
    pattern_split = re.compile(';\s*')    # split on ;<whitespace>
    
    query = pattern_comment.sub("\n\n", query);
    conn = db()
    
    for query in pattern_split.split(query):
        query = query.strip();
        if len(query) > 0:
            debug(query, module = "raw-query")
            o = conn.execute(query)           
