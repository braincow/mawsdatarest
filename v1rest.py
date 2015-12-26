import cherrypy
import dateutil.parser
import pytz
import io

from mongoengine import Q
import matplotlib.pyplot as plt

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
            try:
                # timestamp needs to be a Python datetime object
                row["timestamp"] = dateutil.parser.parse(row["timestamp"]).astimezone(pytz.utc)
                # if the incoming json is in correct format just simply expanding the dictionary keys and values should fill out all necessary variables
                #@TODO: sanitize so that expanded key=value pairs are _only_ those expected
                dbobj = MAWSData(**row).save()
                success = success + 1
            except Exception as e:
                failed = failed + 1

        # construct ack message and return it back to client
        result = {
            'response_type': 'maws_insert',
            # define to success result how many items were added to database
            'maws_insert': {'success': success, 'failed': failed}
        }
        return dict(rest_header_json(), **result)

class PLOTAPIRoot(object):
    exposed = True

    def GET(self, object, startdate, enddate):
        plt.figure()
        x_series = []
        y_series = []
        for datapoint in MAWSData.objects(Q(timestamp__gte=dateutil.parser.parse(startdate)) & Q(timestamp__lte=dateutil.parser.parse(enddate))):
            x_series.append(datapoint["timestamp"].timestamp())
            y_series.append(datapoint[object])
        # plot the graf
        plt.plot(x_series, y_series, label=object)
        plt.legend(loc="upper left")
        plt.xlabel("Date")
        plt.ylabel("Value")
        plt.title("Plotted graph")
        # do some in-memory I/O trickery to get the image out
        buf = io.BytesIO()
        plt.gcf().savefig(buf, format='png')
        buf.seek(0)

        # finally send correct header and pump the bitstream out
        cherrypy.response.headers["Content-Type"] = "image/png"
        return buf.read()
# eof
