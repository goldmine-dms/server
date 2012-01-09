#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *

class CoreStudy(Model):
    __storm_table__ = "corestudies"
    __storm_primary__ = "core_id", "study_id"
    
    core_id = UUID()
    study_id = UUID()
        
    
