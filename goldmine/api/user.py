#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
User functions
"""
from goldmine import *
from goldmine.db import db
from goldmine.models import *
from goldmine.controller import *

@apimethod.auth(who="uuid")
def get(who):
    """ Get the requested user struct """
    who = uuid(who)
    return db().get(auth.User, who)

@apimethod.auth
def whoami():
    return user

@apimethod.auth("user.create")
def create(username, fullname, email, password):
    u = auth.User()
    u.username = username
    u.fullname = fullname
    u.email = email
    u.set_password(password)

    return db().add(u)
