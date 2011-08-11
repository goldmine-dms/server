#!/usr/bin/env python
#-*- coding:utf-8 -*-

import mimetypes
import os.path

from goldmine import debug

errorcodes = {}
#errorcodes[-32700] = "500 Parse error"
#errorcodes[-32600] = "400 Invalid Request"
#errorcodes[-32601] = "404 Method Not Found"
#errorcodes[-32602] = "500 Invalid Parameters"
#errorcodes[-32603] = "500 Internal Error"
#errorcodes[-32000] = "500 Server Error"
#errorcodes[-31000] = "500 Unauthorized"

def start_service(services, server="simple", port=8080, address='0.0.0.0', webroot=None):

    def http_service(env, resp):

        path=env["PATH_INFO"]

        if path not in services:
            if webroot is None:       
                # If webroot is not defined, send a server error back
                resp("501 Not Implemented", [("Content-type", "text/html")])
                return ["<h1>501 Not Implemented</h1>",]
            else:
                filename = webroot + path
                debug(env["REQUEST_METHOD"] + " " + path, params=env["REMOTE_ADDR"], module="webserver")

                if os.path.isdir(filename):
                    if filename[-1] != "/":
                        resp("301 Moved", [("Location", path + "/")])
                        return ["<h1>301 Moved</h1>"]
                    filename = os.path.dirname(filename) + "/index.html"
                    
                if not os.path.isfile(filename):
                    resp("404 Not Found", [("Content-type", "text/html")])
                    return ["<h1>404 Not Found</h1>",]
                
                (mime, enc) = mimetypes.guess_type(filename)
                if mime is None:
                    mime = "application/octet-stream"
                    
                resp("200 OK", [("Content-type", mime)])
                
                f = file(filename,'rb')
                ret = [f.read(),]
                f.close()
                return ret
        
        else:

            if env["REQUEST_METHOD"] != "POST":
                resp("405 Method Not Allowed", [("Content-type", "text/html")])
                return ["<h1>405 Method Not Allowed</h1>",]
            
            try:
                length=int(env.get('CONTENT_LENGTH', '0'))
            except ValueError:
                length=0

            postbody=env['wsgi.input'].read(length)
            
            (out, err) = services[path].handleRequest(postbody)
                        
            if err in errorcodes:
                resp(errorcodes[err], [("Content-type", "application/json-rpc"), ("Content-length", str(len(out)))])
            else:
                resp("200 OK", [("Content-type", "application/json-rpc"), ("Content-length", str(len(out)))])

            return [out]

    if server == "simple":
        from wsgiref.simple_server import make_server
        
        wserver = make_server(address, port, http_service)
        wserver.serve_forever()

        
    elif server == "cherrypy":
        from cherrypy import wsgiserver
    
        wserver = wsgiserver.CherryPyWSGIServer((address, port), http_service, numthreads = 20)

        try:
            wserver.start()
        except KeyboardInterrupt:
            wserver.stop()
    
