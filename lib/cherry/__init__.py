import json
import cherrypy
import os

# utility function to dump REST API http errors out in JSON format instead of HTML
def jsonify_error(status, message, traceback, version):
	error = {
		'application_id': os.environ.get("OPENSHIFT_APP_NAME"),
		'api_method': cherrypy.request.method,
		'api_endpoint': cherrypy.request.path_info,
		'api_version': 1,
		'response_type': 'http_error',
		'http_error': {'status': status, 'message': message}
	}
	cherrypy.response.headers["Content-Type"] = "application/json"
	return json.dumps(error)
