#!/usr/bin/env python
#-*- coding:utf-8 -*-

# for development, run with "autorestart ./http_service.py"
import os

import goldmine

path = os.path.dirname(os.path.abspath(__file__))
config = goldmine.config(path + '/config.ini')

from goldmine.controller import Controller

from goldmine.services.http import HTTPService
from goldmine.protocols.json import JSONRPCProtocol
from goldmine.protocols.rest import RESTProtocol



goldmine.debug("http_service.py started on port %s" % (config["services"]["http"]["port"]), module="http-service")

HTTPService(
    {
        "/service": JSONRPCProtocol(Controller),
        "/json": JSONRPCProtocol(Controller),
        "/rest": RESTProtocol(Controller),
    },
    server=config["services"]["http"]["engine"], 
    port=int(config["services"]["http"]["port"]), 
    webroot=config["services"]["http"]["webroot"]
)

