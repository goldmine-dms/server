#!/usr/bin/env python
#-*- coding:utf-8 -*-

# for development, run with "autorestart ./http_service.py"

import goldmine

from goldmine.controller import Controller

from goldmine.services.http import HTTPService
from goldmine.protocols.json import JSONRPCProtocol
from goldmine.protocols.rest import RESTProtocol

config = goldmine.config('config.ini')

goldmine.debug("http_service.py started on port %s" % (config["services"]["http"]["port"]), module="http_service")

HTTPService(
    {
        "/service": JSONRPCProtocol(Controller),
        "/json": JSONRPCProtocol(Controller),
        "/rest": RESTProtocol(Controller)
    },
    server=config["services"]["http"]["engine"], 
    port=int(config["services"]["http"]["port"]), 
    webroot=config["services"]["http"]["webroot"]
)

