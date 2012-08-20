#!/usr/bin/env python
#-*- coding:utf-8 -*-

# for development, run with "autorestart ./http_service.py"

import goldmine

from goldmine.controller import Controller

from goldmine.services.http import HTTPService
from goldmine.protocols.json import JSONRPCProtocol

config = goldmine.config('config.ini')

goldmine.debug("http_service.py started", module="http_service")

HTTPService(
    {
        "/service": JSONRPCProtocol(Controller)
    },
    server=config["services"]["http"]["engine"], 
    port=int(config["services"]["http"]["port"]), 
    webroot=config["services"]["http"]["webroot"]
)

