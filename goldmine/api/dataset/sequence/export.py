#!/usr/bin/env python
#-*- coding:utf-8 -*-

import datetime
import textwrap

from goldmine import *
from goldmine.db import db
from goldmine.models import *
from goldmine.controller import *

@apimethod
def to_ascii(dataset, commentchar="#"):
    
    metadata = []
    columnmask = ["%12g"]
    
    metadata.append("Exported dataset from Goldmine")
    metadata.append("Export date:    %s" % str(datetime.datetime.now()))
    metadata.append("Goldmine type:  sequence")
    metadata.append("")
    
    
    metadata.append("Created:        %s" % dataset["sequence"]["dataset"]["created"])
    metadata.append("Created by:     %s <%s>" % (dataset["sequence"]["dataset"]["creator"]["fullname"], dataset["sequence"]["dataset"]["creator"]["email"]))
    metadata.append("Index type:     %s" % dataset["sequence"]["index_marker_type"])
    metadata.append("Index location: %s" % dataset["sequence"]["index_marker_location"])
    metadata.append("")
    
    metadata.append("Dataset description:")
    for line in textwrap.wrap(dataset["sequence"]["dataset"]["description"]):
        metadata.append(line)
    
    metadata.append("")
    metadata.append("Columns")
    
    metadata.append(" %s (%s)" % (dataset["sequence"]["index_type"]["name"], dataset["sequence"]["index_type"]["name"]))
    
    for t in dataset["current_parameters"]:
        metadata.append(" %s (%s)" % (t["type"]["name"], t["type"]["unit"]))
        if t["storage"] == "float":
            columnmask.append("%12g")
        else:
            columnmask.append("%12d")
  
    ascii = ""
    data = []  

    for s in metadata:
        ascii += "%s %s\n" % (commentchar, s)
        


    for d in dataset["data"]:
        row = []
        for idx, column in enumerate(d):
            row.append(columnmask[idx] % column)
        data.append(row)

    # optimized string concat
    # method 6 from http://www.skymind.com/~ocrow/python_string/
    ascii += "\n".join([" ".join(line) for line in data])

    return ascii
