#!/usr/bin/env python
#-*- coding:utf-8 -*-

from goldmine import *
from goldmine.db import db
from goldmine.models import *
from goldmine.controller import *

@apimethod(username=str, password=str)
def authenticate(username, password):
    """ Authenticate a user """
    u = db().find(auth.User, auth.User.username == unicode(username)).one()
    if u is None or not u.authenticate(password):
        raise UnauthorizedException("Invalid user or password")
    return auth.Token.create_token(u).id

@apimethod
def version():
    return {"api": 1}

