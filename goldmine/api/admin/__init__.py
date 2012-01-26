#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Admin functions
"""

from goldmine import *
from goldmine.db import db
from goldmine.models import *
from goldmine.controller import *

from goldmine.utils import debugger as _debugger

@apimethod.auth("admin.restart")
def restart():
    """ 
    Restart the server
    FIXME: Only works with CherryPy
    """
          
    import sys, os
    python = sys.executable
    os.execl(python, python, * sys.argv)

@apimethod.auth("admin.debugger")
def debugger():
    """ Drop into a debugger in the current thread """

    print "++++ Debugger requested by", user.username, "++++"
    _debugger()
