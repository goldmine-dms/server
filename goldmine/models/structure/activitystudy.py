#!/usr/bin/env python
#-*- coding:utf-8 -*-

from storm.locals import *
from goldmine.models import *

class ActivityStudy(Model):
    
    __storm_primary__ = "activity_id", "study_id"
    __module__ = "goldmine.models.structure"
    __storm_table__ = "activitystudy"
    
    study_id = UUID()
    activity_id = UUID()
        
    
