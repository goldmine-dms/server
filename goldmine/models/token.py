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
    __export__ = ["id", "ts", ("user", "user_id")]
    
    id = Unicode(primary=True)
    ts = Int()
    valid = Int()
    user_id = UUID()
    user = Reference(user_id, "User.id")
    
    @staticmethod
    def get_user(token_id):
        
        Token.expire_nonvalid()
        token = db().get(Token, token_id)
        
        if token is None:   
            return None
            
        lts = int(time.time())
            
        # dont update the timestamp if the last access time was less than
        # one minute ago.
        
        if token.ts < lts - 60:
            token.ts = lts
            db().commit()
        
        return token.user
        
    @staticmethod
    def create_token(user, valid=timedelta(hours=1)):
        token = Token()
        token.id = unicode(uuid.uuid4().hex)
        token.ts = time.time()
        token.user = user
        
        if valid is not None:
            token.valid = valid.seconds
            
        return db().add(token)
    
    @staticmethod    
    def expire_nonvalid():
        invalid = db().find(Token, Token.valid + Token.ts < int(time.time()))
        for invalid_token in invalid:
            db().remove(invalid_token)
    
    
