import cherrypy

class ForceHTTPSTool(cherrypy.Tool):
	def __init__(self):
		cherrypy.Tool.__init__(self, 'on_start_resource', self.check_https, priority=0)

	def check_https(self):
		if cherrypy.request.scheme == "http":
			https_url = cherrypy.url().replace("http://", "https://")
			raise cherrypy.HTTPRedirect(https_url)

#eof
