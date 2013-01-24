#!/usr/bin/env python
#-*- coding:utf-8 -*-

import mimetypes
import os.path

from goldmine import debug

http_codes = {
    200: "200 OK",
    301: "301 Moved",
    400: "400 Bad Request",
    401: "401 Unauthorized",
    404: "404 Not Found",
    406: "406 Not Acceptable",
    500: "500 Internal Server Error",
    501: "501 Not Implemented"
    
}

def HTTPService(services, server="simple", port=8080, address='0.0.0.0', webroot=None):

    def http_service(env, resp):

        path=env["PATH_INFO"]
        shortpath = path[1:].split("/")
        shortpath = "/" + shortpath[0]
                        
        if shortpath not in services:
            if webroot is None:       
                # If webroot is not defined, send a server error back
                resp(http_codes[501], [("Content-type", "text/html")])
                return ["<h1>HTTP " + http_codes[501] + "</h1>",]
            else:
                filename = webroot + path
                debug(env["REQUEST_METHOD"] + " " + path, params=env["REMOTE_ADDR"], module="webserver")

                if os.path.isdir(filename):
                    if filename[-1] != "/":
                        resp(http_codes[301], [("Location", path + "/")])
                        debug(http_codes[301], params=filename, module="webserver")
                        return ["<h1>HTTP "+http_codes[301]+"</h1>"]
                    filename = os.path.dirname(filename) + "/index.html"
                    
                if not os.path.isfile(filename):
                    resp(http_codes[404], [("Content-type", "text/html")])
                    debug(http_codes[404], params=filename, module="webserver")
                    return ["<h1>HTTP "+http_codes[404]+"</h1>",]
                
                (mime, enc) = mimetypes.guess_type(filename)
                if mime is None:
                    mime = "application/octet-stream"
                    
                resp(http_codes[200], [("Content-type", mime)])
                
                f = file(filename,'rb')
                ret = [f.read(),]
                f.close()
                return ret
        
        else:

            try:
                length=int(env.get('CONTENT_LENGTH', '0'))
            except ValueError:
                length=0

            postbody=env['wsgi.input'].read(length)
            (out, err) = services[shortpath].handleRequest(postbody, env, shortpath)
            resp(http_codes[err], [("Content-type", services[shortpath].content_type), ("Content-length", str(len(out)))])

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

    elif server == "tornado":

        import tornado.httpserver
        import tornado.wsgi

        container = tornado.wsgi.WSGIContainer(http_service)

        http_server = tornado.httpserver.HTTPServer(container)
        http_server.bind(port, address)
        http_server.start(0)
        
        iloop = tornado.ioloop.IOLoop.instance()

        try:
            iloop.start()
        except KeyboardInterrupt:
            iloop.stop()

    else:
        print "Invalid HTTP server selected, exiting"