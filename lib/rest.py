import cherrypy
import json

def rest_header_json(version=1):
    header = {
        'api_id': cherrypy.config.get("app.name"),
        'api_method': cherrypy.request.method,
        'api_endpoint': cherrypy.request.path_info,
        'api_version': version
    }
    return header

def parse_incoming_json():
    # fetch the json content sent in with the request
    try:
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        json_body = json.loads(rawbody.decode("utf-8"))
    except ValueError as e:
        raise cherrypy.HTTPError(400, "Unable to parse HTTP POSTed JSON from request body")
    return json_body

def verify_incoming_json(json_body, accepted_version, accepted_query_type, accepted_payload_type):
    # the POSTed JSON should have an header present, check for validity
    if 'api_id' not in json_body.keys() or 'api_version' not in json_body.keys():
        raise cherrypy.HTTPError(400, "API query header malformed")
    if json_body["api_version"] is not accepted_version:
        raise cherrypy.HTTPError(400, "API version specified not available for this endpoint")
    if json_body["api_id"] != cherrypy.config.get("app.name"):
        raise cherrypy.HTTPError(400, "API id specified not available for this endpoint")

    # all headers should specify what payload type they are sending and it should be present
    if 'query_type' not in json_body.keys():
        raise cherrypy.HTTPError(400, "API query type not specified")
    if accepted_query_type != json_body["query_type"]:
        raise cherrypy.HTTPError(400, "API query type '%s' not accepted for this endpoint" % json_body["query_type"])
    if json_body["query_type"] not in json_body.keys() or json_body["query_type"] is None:
        raise cherrypy.HTTPError(400, "API query payload for type '%s' not present or it is empty" % json_body["query_type"])
    if type(json_body[json_body["query_type"]]) is not accepted_payload_type:
        raise cherrypy.HTTPError(400, "API query payload for type '%s' is not of accepted format" % json_body["query_type"])

    # return the parsed payload only
    return json_body[json_body["query_type"]]
