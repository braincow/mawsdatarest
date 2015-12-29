import cherrypy
import dateutil.parser
import pytz
import io
import matplotlib.pyplot as plt
from mongoengine import Q
from mongoengine.errors import ValidationError, NotUniqueError

from lib.rest import rest_response_json, verify_incoming_json
from lib.db.documents import MAWSData

class MAWSDataRequest(object):
    objects = None
    location = None
    parameter = None

def _fetch_object_data(obj, startdate, enddate, max = 0):
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

        # check basic error with dates being backwards
        if startdate > enddate:
            raise cherrypy.HTTPError(400, "Start date cannot be after end date.")

        # if maximum limit is defined
        if (enddate - startdate).days > max and max > 0:
            raise cherrypy.HTTPError(400, "Trying to acquire too large dataset. Maximum amount of days is %i" % max)

        # start gathering the data
        objects = MAWSData.objects(
            Q(timestamp__gte = startdate) &
            Q(timestamp__lte = enddate) &
            Q(site = loc))
        if objects.__len__() == 0:
            raise cherrypy.HTTPError(404, "With specified parameters no data could be found.")

        cherrypy.request.mawsdata = MAWSDataRequest()
        cherrypy.request.mawsdata.objects = objects
        cherrypy.request.mawsdata.parameter = param
        cherrypy.request.mawsdata.location = loc

class MAWSAPIRoot(object):
    exposed = True

    @cherrypy.tools.auth_basic(realm='MAWSAPIRoot.PUT')
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def PUT(self):
        # fetch json body, check JSON headers and
        #  throw exceptions that we do not catch if there is a problem
        query_payload = verify_incoming_json(
            json_body=cherrypy.request.json,
            accepted_version=1,
            accepted_query_type="maws_insert",
            accepted_payload_type=list)

        skipped = 0
        success = 0
        for row in query_payload:
            try:
                # timestamp needs to be a Python datetime object
                row["timestamp"] = dateutil.parser.parse(row["timestamp"]).astimezone(pytz.utc)
            except ValueError as e:
                raise cherrypy.HTTPError(400, "Unable to parse timestamp. Recommended format is: '0000-00-00T00:00:00.00+00:00' or any other ISO compatible presentation.")

            # sanitize so that expanded key=value pairs are _only_ those expected
            accepted_keys = list(MAWSData._db_field_map.keys())
            accepted_keys.remove('id')
            for received_key in row.keys():
                if received_key not in accepted_keys:
                    raise cherrypy.HTTPError(400, "Syntax error. Unexpected key '%s'" % received_key)

            # if the incoming json is in correct format just simply expanding the dictionary keys and values should fill out all necessary variables
            try:
                dbobj = MAWSData(**row).save()
                success = success + 1
            except ValidationError as e:
                raise cherrypy.HTTPError(400, str(e))
            except NotUniqueError as e:
                skipped = skipped + 1

        # construct ack message and return it back to client
        result = {
            # define to success result how many items were added to database
            'maws_insert': {'success': success, 'skipped': skipped}
        }
        return rest_response_json(version=1, payload=result)

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def GET(self, obj, startdate, enddate):
        # parse parameters, fetch data
        _fetch_object_data(
            obj=obj, startdate=startdate, enddate=enddate,
            max=cherrypy.config.get("plot.max.days"))
        objects = cherrypy.request.mawsdata.objects
        param = cherrypy.request.mawsdata.parameter
        loc = cherrypy.request.mawsdata.location
        datapoints = dict()
        for datapoint in objects:
            datapoints[datapoint["timestamp"].replace(tzinfo=pytz.UTC).isoformat()] = datapoint[param]
        result = {
            # define result
            'maws_data': {
                'location': loc,
                'parameter': param,
                'datapoints': datapoints
            }
        }
        return rest_response_json(version=1, payload=result)

class PLOTAPIRoot(object):
    exposed = True

    def GET(self, obj, startdate, enddate):
        # parse parameters, fetch data
        _fetch_object_data(
            obj=obj, startdate=startdate, enddate=enddate,
            max=cherrypy.config.get("plot.max.days"))
        objects = cherrypy.request.mawsdata.objects
        param = cherrypy.request.mawsdata.parameter

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
