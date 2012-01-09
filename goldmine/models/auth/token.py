#!/usr/bin/env python
#-*- coding:utf-8 -*-

import uuid
import time
from datetime import timedelta

from storm.locals import *
from goldmine.models import *
from goldmine.db import db

class Token(Model):

    __storm_table__ = "tokens"
    __export__ = ["id", "timestamp", ("user", "user_id")]
    
    id = Unicode(primary=True)
    timestamp = Int()
    validity = Int() # None means forever valid
    user_id = UUID()
    user = Reference(user_id, "auth.User.id")
    
    @staticmethod
    def get_user(token_id):
        
        Token.expire_nonvalid()
        token = db().get(Token, token_id)
        
        if token is None:   
            return None
            
        now = int(time.time())
            
        # dont update the timestamp if the last access time was less than
        # one minute ago.
        
        if token.timestamp < now - 60:
            token.timestamp = now
            db().commit()
        
        return token.user
        
    @staticmethod
    def create_token(user, valid=timedelta(hours=1)):
        token = Token()
        token.id = unicode(uuid.uuid4().hex)
        token.timestamp = time.time()
        token.user = user
        
        if valid is not None:
            token.validity = valid.seconds
            
        return db().add(token)
    
    @staticmethod    
    def expire_nonvalid():
        invalid = db().find(Token, Token.validity + Token.timestamp < int(time.time()))
        for invalid_token in invalid:
            db().remove(invalid_token)
    
    
