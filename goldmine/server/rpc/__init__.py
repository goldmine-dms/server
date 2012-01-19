#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Functions exposed over RPC interface
"""




from goldmine import *
from goldmine.db import db
from goldmine.models import *

from goldmine.server.service import Unauthorized, rpc

"""
Non-authenticated functions (main namespace)
"""

@rpc
def authenticate(username, password):
    """ Authenticate a user """
    u = db().find(auth.User, auth.User.username == unicode(username)).one()
    if u is None or not u.authenticate(password):
        raise Unauthorized("Invalid user or password")
    return auth.Token.create_token(u).id

@rpc
def version():
    return {"api": 1}

"""
Authenticated functions (in namespaces)
"""

import goldmine.server.rpc.admin
import goldmine.server.rpc.core
import goldmine.server.rpc.dataset
import goldmine.server.rpc.site 
import goldmine.server.rpc.study
import goldmine.server.rpc.type
import goldmine.server.rpc.user
