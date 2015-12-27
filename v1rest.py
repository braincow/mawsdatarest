import cherrypy
import dateutil.parser
import pytz
import io

from mongoengine import Q
import matplotlib.pyplot as plt

from lib.rest import rest_response_json, verify_incoming_json
from lib.db.documents import MAWSData

class MAWSAPIRoot(object):
    exposed = True

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def PUT(self):
        # fetch json body, check JSON headers and
        #  throw exceptions that we do not catch if there is a problem
        query_payload = verify_incoming_json(
            json_body=cherrypy.request.json,
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
            # define to success result how many items were added to database
            'maws_insert': {'success': success, 'failed': failed}
        }
        return rest_response_json(version=1, payload=result)

class PLOTAPIRoot(object):
    exposed = True

    def GET(self, obj, startdate, enddate):
        # verify that object field is defined correctly
        try:
            loc, param = obj.split(":")
        except ValueError as e:
            raise cherrypy.HTTPError(400, "Object needs to be defined in site:value format")

        # verify that startdate and enddate are correct
        try:
            startdate = dateutil.parser.parse(startdate)
            enddate = dateutil.parser.parse(enddate)
        except ValueError as e:
            raise cherrypy.HTTPError(400, "End and/or start date defined incorrectly. Recommended format is: '0000-00-00T00:00:00.00+00:00' or any other ISO compatible presentation.")

        # start gathering data to plot
        objects = MAWSData.objects(
            Q(timestamp__gte = startdate) &
            Q(timestamp__lte = enddate) &
            Q(site = loc))
        if objects.__len__() == 0:
            raise cherrypy.HTTPError(404, "With specified parameters no data could be found to be plotted.")
        # plot the graf
        x_series = []
        y_series = []
        for datapoint in objects:
            x_series.append(datapoint["timestamp"].timestamp())
            y_series.append(datapoint[param])
        plt.figure()
        plt.plot(x_series, y_series, label=obj)
        plt.legend(loc="upper left")
        plt.xlabel("Relative timestamp")
        plt.ylabel("Value of plotted object")
        plt.title("Plotted graph")
        # do some in-memory I/O trickery to get the image out
        buf = io.BytesIO()
        plt.gcf().savefig(buf, format='png')
        buf.seek(0)

        # finally send correct header and pump the bitstream out
        cherrypy.response.headers["Content-Type"] = "image/png"
        return buf.read()

# eof
