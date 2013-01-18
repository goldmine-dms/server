#!/usr/bin/env python
#-*- coding:utf-8 -*-

import inspect

from goldmine import *
from goldmine.db import db
from goldmine.models import *
from goldmine.controller import *

@apimethod
def methods():
    return [method.fqn[len(API_NAMESPACE)+1:] for method in exposed_methods]

@apimethod
def help(query):

    # FIXME: fail less gracefully, with an exception

    rv = None
    for method in exposed_methods:
        if unicode(method.fqn[len(API_NAMESPACE)+1:]) == query:
            arguments = inspect.formatargspec(*inspect.getargspec(method))
            rv = "%s%s" % (query, arguments)
            if method.func_doc: rv += "\n%s" % method.func_doc 
    return rv
