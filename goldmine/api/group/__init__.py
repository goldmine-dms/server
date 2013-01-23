"""
Group functions
"""

from goldmine import *
from goldmine.db import db
from goldmine.models import *
from goldmine.controller import *

@apimethod.auth
def get(group_id):
    """ Get the requested group struct """
    group_id = uuid(group_id, user)
    return db().get(auth.Group, group_id)

@apimethod.auth
def all():
    rs = db().find(auth.Group).order_by(auth.Group.name)
    return rs_to_list(rs)

@apimethod.auth("group.create")
def create(name, parent_id=None):
    u = auth.Group()
    u.name = name

    if parent_id:
        u.parent_id = uuid(parent_id)
    
    return db().add(u)

@apimethod.auth
def add_member(group_id, user_id):
    """
        Add user to group
    """

    group_id = uuid(group_id, user)
    user_id = uuid(user_id, user)

    # FIXME: security

    gm = auth.GroupMember()
    gm.user_id = user_id
    gm.group_id = group_id

    return db().add(gm)

@apimethod.auth
def remove_member(group_id, user_id):
    """
        Remove user from group, but it cannot be yourself (unless you are an admin)
    """

    group_id = uuid(group_id, user)
    user_id = uuid(user_id, user)

    # FIXME: security

    rs = db().find(auth.GroupMember, auth.GroupMember.group_id == group_id, auth.GroupMember.user_id == user_id)
    gm = rs.one()

    if gm is None:
        raise TypeError("Group membership not found")

    if gm.user == user and not user.is_admin():
        raise TypeError("You cannot remove yourself from a group")

    db().remove(gm)




@apimethod.auth
def memberships(user_id=None, explicit=False):
    
    """ 
        List group memberships for user

        user_id:    user_id of queried user
                    None for current user

        explicit:   List only explicit memberships

    """

    if user_id:
        user_id = uuid(user_id, user)
    else:
        user_id = user.id

    memberships = set()
    rs = db().find(auth.GroupMember, auth.GroupMember.user_id == user_id)

    for group in rs:
        memberships.add(group.group)

    if explicit:
        return list(memberships)

    implicit = set()
    for ms in memberships:
        while ms.parent:
            implicit.add(ms.parent)
            ms = ms.parent

    return rs_to_list(memberships.union(implicit)) 


@apimethod.auth
def has_member(group_id, user_id=None, explicit=False):
    
    """ 
        Is user a member of group

        group_id:   group_id of queried group

        user_id:    user_id of queried user
                    None for current user

        explicit:   only explicit memberships
    """

    group_id = uuid(group_id, user)
    group = db().get(auth.Group, group_id)

    if user_id:
        user_id = uuid(user_id, user)
    else:
        user_id = user.id

    for member in group.members:
        if member.id == user_id: return True
        
    if explicit:
        return False
    else:
        return _implicit_member(group, user_id)


def _implicit_member(group, user_id):
    """
        Find if user is an implicit member of group
    """
    for child in group.children:
        for member in child.members:
            if member.id == user_id: return True
        if _implicit_member(child, user_id):
            return True
    return False
        

@apimethod.auth
def tree():
    """ Get a tree of all groups """
    groups = db().find(auth.Group, auth.Group.parent_id == None)
    objs = []
    for group in groups:
        obj = _subtree(group)
        objs.append(obj)

    return objs

def _subtree(group):
    obj = {}
    obj["id"] = unicode(group.id)
    obj["name"] = group.name
    obj["children"] = map(_subtree, group.children)
    return obj