#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
User.Settings functions
"""

from goldmine import *
from goldmine.db import db
from goldmine.models import *
from goldmine.controller import *

@apimethod.auth
def get(setting):
    """ Get the specific user setting """
    return setting
    #who = uuid(who)
    #return db().get(auth.User, who)
    
