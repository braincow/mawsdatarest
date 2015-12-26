import cherrypy
import dateutil.parser
import pytz

from lib.rest import rest_header_json, parse_incoming_json, verify_incoming_json
from lib.db.documents import MAWSData

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

        failed = 0
        success = 0
        for row in query_payload:
#            try:
            # timestamp needs to be a Python datetime object
            row["timestamp"] = dateutil.parser.parse(row["timestamp"]).astimezone(pytz.utc)
            # if the incoming json is in correct format just simply expanding the dictionary keys and values should fill out all necessary variables
            #@TODO: sanitize so that expanded key=value pairs are _only_ those expected
            dbobj = MAWSData(**row).save()
            success = success + 1
#            except Exception as e:
#                failed = failed + 1

        # construct ack message and return it back to client
        result = {
            'response_type': 'maws_insert',
            # define to success result how many items were added to database
            'maws_insert': {'success': success, 'failed': failed}
        }
        return dict(rest_header_json(), **result)

    @cherrypy.tools.json_out()
    def GET(self):
        #@TODO: get requested data from database and return JSON from it
        return dict(rest_header_json())

# eof
