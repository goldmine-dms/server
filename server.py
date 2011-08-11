#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os

import goldmine
config = goldmine.config('config.ini')

from goldmine.server.http_service import start_service
from goldmine.server.service import JSONRPCService
from goldmine.server import rpc

if __name__ == '__main__':

    # Start the RPC service
    goldmine.debug("Starting server", module="rpcserver")
    start_service({"/service": JSONRPCService(rpc)}, "cherrypy", port=8080, webroot=os.getcwd()+"/../client/www")

