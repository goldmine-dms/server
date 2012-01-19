#!/usr/bin/env python
#-*- coding:utf-8 -*-

import datetime

from storm.locals import *
from goldmine.models import *
from goldmine.db import generate_uuid, db

class Metadata(Model):

    __export__ = ["id", ("dataset", "dataset_id"), "metadata_type", "metadata_handler", "created", ("created_by", "created_by_id"), "metadata"]
    
    id = UUID(primary=True, default_factory=generate_uuid)
    dataset_id = UUID()
    
    metadata_type = Enum(map={"annotation": 1, "keyvalue": 2, "tag": 3})
    metadata_handler = Enum(map={"generic": 1, "typehandled": 2})
     
    created = DateTime(default_factory=datetime.datetime.now)
    created_by_id = UUID()
        
    dataset = Reference(dataset_id, "dataset.Dataset.id")
    created_by = Reference(created_by_id, "auth.User.id")
    
    annotation = Reference(id, "metadata.Annotation.metadata_id")
    tag = Reference(id, "metadata.Tag.metadata_id")
    keyvalue = ReferenceSet(id, "metadata.KeyValue.metadata_id")
    
    @property
    def metadata(self):
        if self.metadata_type == "annotation":
            return self.annotation
        elif self.metadata_type == "keyvalue":
            return self.keyvalue
        elif self.metadata_type == "tag":
            return self.tag
            
    @metadata.setter
    def metadata(self, obj):
        if self.metadata_type == "annotation":
            a = metadata.Annotation()
            a.annotation = obj
            db.add(a)
        elif self.metadata_type == "keyvalue":
            for key in obj:
                kv = metadata.KeyValue()
                kv.key = key
                kv.value = obj[key]
                kv.metadata_id = self.id
                db.add(entry)
        elif self.metadata_type == "tag":
            t = metadata.Tag()
            t.tag = obj
            db.add(t)
