#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid, db

class KeyValue(Model):

    __storm_table__ = "metadata_keyvalue"
    __export__ = ["id", "key", "value", "holds"]
    
    id = UUID(primary=True, default_factory=generate_uuid)
    metadata_id = UUID()
    key = Unicode()
    holds = Enum(map={"float": 1, "int": 2, "string": 3})
    value_float = Float()
    value_int = Int()
    value_string = Unicode()

    @property
    def value(self):
        if self.holds == "float":
            return self.value_float
        elif self.holds == "int":
            return self.value_int
        elif self.holds == "string":
            return self.value_string
            
    @value.setter
    def value(self, val):
        if isinstance(val, float):
            self.value_float = val
            self.holds = "float"
        elif isinstance(val, int):
            self.value_int = val
            self.holds = "int"
        elif isinstance(val, str):
            self.value_string = val
            self.holds = "string"
        else:
            raise Exception("The value for key %s must be either float, int or string" % self.key)
