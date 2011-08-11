#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
User functions
"""

from goldmine import *
from goldmine.db import db
from goldmine.models import *

from goldmine.server import needauth
from goldmine.server.service import Unauthorized

@needauth
def whoami(user):
    return user

@needauth
def user_info(who):
    who = uuid(who)
    return db().get(User, who)

@needauth
def create(username, fullname, email, password, user):
    #FIXME: Add authentication
    u = User()
    u.username = username
    u.fullname = fullname
    u.email = email
    
    u.set_password(password)

    return db().add(u)
