import json
import cherrypy

# utility function to dump REST API http errors out in JSON format instead of HTML
def jsonify_error(status, message, traceback, version):
	error = {
		'api_version': 1,
		'response_type': 'http_error',
		'http_error': {'status': status, 'message': message}
	}
	cherrypy.response.headers["Content-Type"] = "application/json"
	return json.dumps(error)
