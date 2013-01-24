#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" Usage: http_service.py [--config=<config>] [--engine=<engine>] [<port>] """

import os
import docopt

import goldmine

options = docopt.docopt(__doc__)

if options["--config"]:
    configfile = options["--config"]
else:
    path = os.path.dirname(os.path.abspath(__file__))
    configfile = path + '/config.ini'

config = goldmine.config(configfile)

if options["<port>"]:
    config["services"]["http"]["port"] = options["<port>"]

if options["--engine"]:
    config["services"]["http"]["engine"] = options["--engine"]

from goldmine.controller import Controller

from goldmine.services.http import HTTPService
from goldmine.protocols.json import JSONRPCProtocol
from goldmine.protocols.rest import RESTProtocol


info = (config["services"]["http"]["port"], config["services"]["http"]["engine"])
goldmine.debug("http_service.py starting on port %s with %s" % info, module="http-service")

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

