import cherrypy

from lib.rest import rest_header_json, parse_incoming_json, verify_incoming_json

class MAWSAPIRoot(object):
    exposed = True

    @cherrypy.tools.json_out()
    def PUT(self):
        # fetch json body, check JSON headers and
        #  throw exceptions that we do not catch if there is a problem
        json_body = parse_incoming_json()
        query_payload = verify_incoming_json(
            json_body=json_body,
            accepted_version=1,
            accepted_query_type="maws_insert",
            accepted_payload_type=list)

        for row in query_payload:
            #@TODO: create database object for each row and store it in database
            pass

        # construct ack message and return it back to client
        result = {
            'response_type': 'success',
            # define to success result how many items were added to database
            'success': dict()
        }
        return dict(rest_header_json(), **result)

    @cherrypy.tools.json_out()
    def GET(self):
        #@TODO: get requested data from database and return JSON from it
        return dict(rest_header_json)

# eof
