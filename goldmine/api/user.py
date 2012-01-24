#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
User functions
"""
from goldmine import *
from goldmine.db import db
from goldmine.models import *
from goldmine.controller import apimethod

@apimethod.auth
def whoami():
    return user

@apimethod.auth(who=str)
def user_info(who):
    who = uuid(who)
    return db().get(User, who)

@apimethod.auth("user.create", username=str, fullname=str, email=str, password=str)
def create(username, fullname, email, password):
    #FIXME: Add authentication
    u = User()
    u.username = username
    u.fullname = fullname
    u.email = email
    u.set_password(password)

    return db().add(u)
