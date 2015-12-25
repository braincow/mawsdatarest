import json
import cherrypy

from lib.rest import rest_header_json

# utility function to dump REST API http errors out in JSON format instead of HTML
def jsonify_error(status, message, traceback, version):
	error = {
		'response_type': 'http_error',
		'http_error': {'status': status, 'message': message}
	}
	cherrypy.response.headers["Content-Type"] = "application/json"
	return json.dumps(dict(rest_header_json(), **error))

# eof
