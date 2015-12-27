import cherrypy
import json

from lib.rest import rest_response_json

# utility function to dump REST API http errors out in JSON format instead of HTML
def jsonify_error(status, message, traceback, version):
	error = {
		'http_error': {'status': status, 'message': message}
	}
	cherrypy.response.headers["Content-Type"] = "application/json"
	return json.dumps(rest_response_json(version=1, payload=error))

# eof
