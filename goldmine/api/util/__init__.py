#!/usr/bin/env python
#-*- coding:utf-8 -*-

from goldmine.controller import *

@apimethod
def argmap(listargs, function, *args, **kwargs):
    """
        Helper method for chaining functions, mapping a list as
        non-keyword arguments into the first slots.

        This will call either:  

             function(listargs[0], listargs[1], ..., args[0], args[1], ...)
             function(listargs[0], listargs[1], ..., kw = kwargs["kw"], ...)

        listargs:   data from the previous function
        function:   (string) function to map to
        *args:      (list) a number of extra arguments to add after listargs
        *kwargs:    (dict) a number of extra keyword arguments
    """

    listargs = list(listargs)
    function = resolver.get(function, user)
    listargs.extend(args)
    return function(*listargs, **kwargs)