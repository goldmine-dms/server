#!/usr/bin/env python
#-*- coding:utf-8 -*-

from goldmine import *
from goldmine.db import db
from goldmine.models import *
from goldmine.controller import *

@apimethod(username="string", password="string")
def authenticate(username, password):
    """ 
    Authenticate a user 
    """
    
    u = db().find(auth.User, auth.User.username == unicode(username)).one()
    if u is None or not u.authenticate(password):
        raise UnauthorizedException("Invalid user or password")
    return auth.Token.create_token(u).id

@apimethod
def info():
    """
    Get information about the service
    """

    c = config()

    rv = {
        "version": {"api": 2},
        "server": {
            "name": c["server"]["name"], 
            "organisation": c["server"]["organisation"]
        }
    }
    
    return rv


@apimethod.auth
def chain(*chainspec):
    """
    Chain multiple functions together
        
    The chain specification
    -----------------------
    
    The chain specification consists of multiple hops, represented by a list
    
        [hop_0, hop_1, hop_2, ... hop_n]
        
    Each hop is defined as:
        
        ["func"] = (list) function "func" called without extra parameters
        ["func", paramspec] = (list) function "func" called with extra 
                                     parameters, defined in paramspec
                                     
    The first positional parameter passed to the function is always the 
    result of the previous function call, such:
        
        hop_2(hop_1(hop_0(param0), param1), param2)
                                     
    A paramspec is defined as
    
        ["a", 1] = (list) calling the function with extra parameters ("a", 1)
        {"a": 1} = (dict) calling the function with extra parameters ("a" = 1)
        "a"      = (any type) calling the function with a single extra param
    
    This means that a chain spec of:
    
        [["func_a", "param_a"], ["func_b", {"param_b": 22}]]
    
    is results in the following call:
    
        func_b(func_a("param_a"), param_b = 22)
        
    and the value of the call is returned to the user.
    
    Branching
    ---------
    
    The chain can merge as an inverted tree, such that it is possible
    to combine outputs of multiple functions into the arguments of a new
    function.
    
    The result of the multiple functions will always be placed at the 
    first positional parameter of the receving function.
    
    The following chainspec:
    
        [[["hop_0"], ["hop_1"]], ["hop_2"]]
    
    Results in the following call
    
        hop_2( [hop_0(), hop_1()] )
        
    The chain can also branch out, providing a duplicate of the previous
    result to each of the branches:
    
        [["hop_0"], [["hop_1"], ["hop_2"]]]
    
    Results in the following call
    
        [hop_1(hop_0), hop_2(hop_0)]
        
    Chains can be nested as well.
    
    """
    
    # most of the functionality is implemented in 
    # "chain_with_input", below
    
    chainspec = list(chainspec)
    chainspec.insert(0, None)
    return resolver.get("chain_with_input", user)(*chainspec)
    
    
@apimethod.auth
def chain_with_input(inputdata, *chainspec):
    """
    Chain multiple functions together, with initial input data
    
    inputdata = initial input for the functions, if None, it is not passed
    *chainspec = specification of the chained functions
    
    See chain(*chainspec) for documentation
    """
    
    result = inputdata
       
    for hop in chainspec:

        params = None
        if type(hop) in [list, tuple]:
            if type(hop[0]) in [list, tuple]:
                
                # Branching detected                                
                chain_fn = resolver.get("chain_with_input", user)
                branch_result = []
                
                for branch in hop:                     
                    if type(branch[0]) in [list, tuple]: # multihop chainspec
                        if result is None:
                            branch.insert(0, None)
                        else:
                            branch.insert(0, result)
                        branch_result.append(chain_fn(*branch))
                    else: # singlehop chainspec
                        if result is None:
                            branch_result.append(chain_fn(None, branch))
                        else:
                            branch_result.append(chain_fn(result, branch))
                
                result = branch_result
                continue
            
            method = hop[0]
            
            if len(hop) > 2:
                raise TypeError("Each hop in the chain must have one or two elements")
            if len(hop) == 2:
                params = hop[1]
        else:
            raise TypeError("Invalid hop in specified chain")
        
        if result is None:
            fn = resolver.get(method, user)
        else:
            fn = lambda *args, **kwargs: resolver.get(method, user)(result, *args, **kwargs)  
       
        if params is None:
            result = fn()
        elif type(params) in [list, tuple]:
            result = fn(*params)
        elif type(params) is dict:
            result = fn(**params)
        else:
            result = fn(params)
   
    return result


    
    
