#!/usr/bin/env python
#-*- coding:utf-8 -*-

import bcrypt

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid

class User(Model):

    __storm_table__ = "user"
    __export__ = ["id", "username", "fullname", "email", "userlevel"]
    
    id = UUID(primary=True, default_factory=generate_uuid)
    username = Unicode()
    fullname = Unicode()
    email = Unicode()
    password = Unicode()
    userlevel = Int(default=1)
  
    def is_admin(self):
        return (self.userlevel >= 10)

    def authenticate(self, password):
        return bcrypt.hashpw(password, self.password) == self.password

    def set_password(self, password):
        self.password = unicode(bcrypt.hashpw(password, bcrypt.gensalt()))
