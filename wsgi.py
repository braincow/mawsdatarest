#!/usr/bin/python
import os
import sys
import cherrypy

from mongoengine import connect

# tool to force HTTPS connections for content that needs to be protected on-route
from lib.cherry.https import ForceHTTPSTool
cherrypy.tools.forcehttps = ForceHTTPSTool()

# tool used to fetch MAWS data objects from database and put them part as cherrypy.request
from lib.cherry.mawsdata import MAWSDataTool
cherrypy.tools.fetch_mawsdata = MAWSDataTool()

# approot object should be the root page of our application
from v1rest import MAWSAPIRoot, PLOTAPIRoot
class v1APIRoot(object):
    exposed = True
    maws = MAWSAPIRoot()
    plot = PLOTAPIRoot()

class APIRoot(object):
    exposed = True
    v1 = v1APIRoot()

class MAWSdataWebRoot(object):
    api = APIRoot()

    @cherrypy.expose
    def index(self):
        return None

approot = MAWSdataWebRoot

# use configs here as application config for this cherrypy application
configdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config')

if __name__ != "__main__":
	import atexit
	# start cherrypy engine and stuff
	cherrypy.config.update(os.path.join(configdir, 'cherrypy_wsgi.conf'))
	connect(cherrypy.config.get("mongodb.def"), host=cherrypy.config.get("mongodb.uri"))
	cherrypy.server.unsubscribe()
	cherrypy.engine.start()
	atexit.register(cherrypy.engine.stop)
	appconfig = os.path.join(configdir, "application_wsgi.conf")
	# create and start WSGI application framework / application by CherryPy
	application = cherrypy.Application(approot(), script_name=None, config=appconfig)
else:
	# start cherrypy locally
	cherrypy.config.update(os.path.join(configdir, 'cherrypy_standalone.conf'))
	connect(cherrypy.config.get("mongodb.def"), host=cherrypy.config.get("mongodb.uri"))
	appconfig = os.path.join(configdir, "application_standalone.conf")
	cherrypy.quickstart(approot(), '/', config=appconfig)

#eof
