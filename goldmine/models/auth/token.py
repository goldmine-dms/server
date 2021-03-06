#!/usr/bin/env python
#-*- coding:utf-8 -*-

import uuid
import time
from datetime import timedelta

from goldmine.utils import retry
from storm.locals import *
from goldmine.models import *
from goldmine.db import db

class Token(Model):

    __storm_table__ = "token"
    __export__ = ["id", "timestamp", ("user", "user_id")]
    __module__ = "goldmine.models.auth"
    
    id = Unicode(primary=True)
    timestamp = Int()
    validity = Int() # None means forever valid
    user_id = UUID()
    user = Reference(user_id, "auth.User.id")
    
    @staticmethod
    @retry(Exception)
    def get_user(token_id):
        try:
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
        except:
            db().rollback()
            raise
        
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
            
    @staticmethod
    def expire(user):
        tokens = db().find(Token, Token.user == user, Not(Token.validity == None))
        for token in tokens:
            db().remove(token)
    
    
