#!/usr/bin/env python
#-*- coding:utf-8 -*-

import goldmine

from goldmine.controller import Controller

from goldmine.services.http import HTTPService
from goldmine.protocols.json import JSONRPCProtocol

config = goldmine.config('config.ini')

HTTPService(
    {
        "/service": JSONRPCProtocol(Controller)
    },
    server=config["server"], 
    port=int(config["port"]), 
    webroot=config["www_client"]
)

