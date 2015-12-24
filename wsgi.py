#!/usr/bin/python
import os

# load webapp framework
import cherrypy

# load and connect to database
from mongoengine import connect

# tool to force HTTPS connections for content that needs to be protected on-route
from lib.cherry.https import ForceHTTPSTool
cherrypy.tools.forcehttps = ForceHTTPSTool()

# approot object should be the root page of our application
class mawsdata(object):
    @cherrypy.expose
    def index(self):
        pass
approot = mawsdata

# use configs here as application config for this cherrypy application
configdir = os.path.join(os.environ.get("OPENSHIFT_REPO_DIR"), 'config')

if __name__ != "__main__":
	import atexit
	# start cherrypy engine and stuff
	cherrypy.config.update(os.path.join(configdir, 'cherrypy_openshift.conf'))
	connect(cherrypy.config.get("mongodb.def"), host=cherrypy.config.get("mongodb.uri"))
	cherrypy.server.unsubscribe()
	cherrypy.engine.start()
	atexit.register(cherrypy.engine.stop)
	appconfig = os.path.join(configdir, "%s_%s" % (os.environ.get("OPENSHIFT_APP_NAME"), 'openshift.conf'))
	# create and start WSGI application framework / application by CherryPy
	application = cherrypy.Application(approot(), script_name=None, config=appconfig)
else:
	# start cherrypy locally
	cherrypy.config.update(os.path.join(configdir, 'cherrypy_localhost.conf'))
	connect(cherrypy.config.get("mongodb.def"), host=cherrypy.config.get("mongodb.uri"))
	appconfig = os.path.join(configdir, "%s_%s" % (os.environ.get("OPENSHIFT_APP_NAME"), 'localhost.conf'))
	cherrypy.quickstart(approot(), '/', config=appconfig)

#eof
