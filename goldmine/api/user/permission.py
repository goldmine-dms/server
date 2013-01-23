#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
User Permissions functions
"""

from goldmine import *
from goldmine.db import db
from goldmine.models import *
from goldmine.controller import *


@apimethod.auth("user.permission.grant")
def grant(user_id, identifier):
    """ Grant a permission """
    user_id = uuid(user_id, user)
    p = auth.Permission()
    p.user_id = user_id
    p.identifier = identifier
    p.granted_by = user
    return db().add(p)


@apimethod.auth("user.permission.grant")
def revoke(user_id, identifier=None):
    """ 
        Revoke a permission

        user_id:        the id of the user to revoke permissions for
        identifier:     the permission as a string
                        None to strip all permissions from user

        returns the number of revoked permissions
    """
    user_id = uuid(user_id, user)

    if identifier:
        revoked = db().find(auth.Permission, auth.Permission.user_id == user_id, auth.Permission.identifier == identifier)
    else:
        revoked = db().find(auth.Permission, auth.Permission.user_id == user_id)

    for perm in revoked:
        db().remove(perm)
    return len(list(revoked))

@apimethod.auth
def access(identifier, user_id=None):
    """
        Check if user has access to permission
    """

    user_id = uuid(user_id, user)

    if not user_id:
        user_id = user.id

    result = db().find(auth.Permission, auth.Permission.user_id == user_id and auth.Permission.identifier == identifier)
    return result.one() is not None

@apimethod.auth
def all():
    """ Get all permissions issued for current user """
    perms = db().find(auth.Permission, auth.Permission.user == user)
    return rs_to_list(perms)

@apimethod.auth
def all_for(user_id):
    """ Get all permissions issued for a specific user """
    user_id = uuid(user_id, user)
    perms = db().find(auth.Permission, auth.Permission.user_id == user_id)
    return rs_to_list(perms)