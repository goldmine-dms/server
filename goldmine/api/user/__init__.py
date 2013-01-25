#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
User functions
"""

from goldmine import *
from goldmine.db import db
from goldmine.models import *
from goldmine.controller import *

@apimethod.auth
def get(user_id):
    """ Get user struct for user_id """
    user_id = uuid(user_id, user)
    return db().get(auth.User, user_id)

@apimethod.auth
def all():
    """ All users """
    rs = db().find(auth.User)
    return rs_to_list(rs)

@apimethod.auth
def whoami():
    return user
    
@apimethod.auth
def logout():
    auth.Token.expire(user)

@apimethod.auth("user.create")
def create(username, fullname, email, password):
    u = auth.User()
    u.username = username
    u.fullname = fullname
    u.email = email
    u.set_password(password)

    return db().add(u)

@apimethod.auth("user.change_userlevel")
def change_userlevel(user_id, level):
    user_id = uuid(user_id, user)
    selected_user = db().get(auth.User, user_id)
    selected_user.userlevel = level
    return selected_user

@apimethod.auth
def change_password(password):
    user.set_password(password)

