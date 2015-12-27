import cherrypy

def rest_response_json(version, payload):
    response_type = list(payload.keys()).pop()
    header = {
        'api_id': cherrypy.config.get("app.name"),
        'api_method': cherrypy.request.method,
        'api_endpoint': cherrypy.request.path_info,
        'api_version': version
    }
    message = dict(dict(header=header), **payload)
    message["header"]["response_type"] = response_type
    return message

def verify_incoming_json(json_body, accepted_version, accepted_query_type, accepted_payload_type):
    # the POSTed JSON should have an header present, check for validity
    if 'header' not in json_body.keys():
        raise cherrypy.HTTPError(400, "API query header missing")
    if 'api_id' not in json_body["header"].keys() or 'api_version' not in json_body["header"].keys():
        raise cherrypy.HTTPError(400, "API query header malformed")
    if json_body["header"]["api_version"] is not accepted_version:
        raise cherrypy.HTTPError(400, "API version specified not available for this endpoint")
    if json_body["header"]["api_id"] != cherrypy.config.get("app.name"):
        raise cherrypy.HTTPError(400, "API id specified not available for this endpoint")
    # all headers should specify what payload type they are sending and it should be present
    if 'query_type' not in json_body["header"].keys():
        raise cherrypy.HTTPError(400, "API query type not specified")
    if accepted_query_type != json_body["header"]["query_type"]:
        raise cherrypy.HTTPError(400, "API query type '%s' not accepted for this endpoint" % json_body["header"]["query_type"])
    # check that query is in there too
    if json_body["header"]["query_type"] not in json_body.keys():
        raise cherrypy.HTTPError(400, "API query payload for type '%s' not present" % json_body["header"]["query_type"])
    if type(json_body[json_body["header"]["query_type"]]) is not accepted_payload_type:
        raise cherrypy.HTTPError(400, "API query payload for type '%s' is not of accepted format" % json_body["header"]["query_type"])

    # return the parsed payload only
    return json_body[json_body["header"]["query_type"]]
