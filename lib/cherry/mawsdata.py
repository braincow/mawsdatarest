import cherrypy
import dateutil.parser

from mongoengine import Q

from lib.db.documents import MAWSData

_MAWS_QUERY_REQUEST_PARAM_POSITION = {
    'obj': 4,
    'startdate': 5,
    'enddate': 6
}

class MAWSDataRequest(object):
    objects = None
    location = None
    parameter = None

    def __init__(self, objects, location, parameter):
        self.objects = objects
        self.location = location
        self.parameter = parameter

def _maws_request_param(name):
    path_info = cherrypy.request.path_info.split("/")
    if name in cherrypy.request.params:
        # if the value is in standard HTTP parameter notation, pull it from there
        retval = cherrypy.request.params.get(name)
    else:
        # if not, try to parse it out of path_info
        try:
            retval = path_info[_MAWS_QUERY_REQUEST_PARAM_POSITION[name]]
        except IndexError as e:
            raise cherrypy.HTTPError(400, "Unable to parse '%s' argument from query parameters" % name)

    # return value if such was found
    return retval

class MAWSDataTool(cherrypy.Tool):
    def __init__(self):
        cherrypy.Tool.__init__(self, 'before_handler', self.tool_hook, priority=1000)

    def tool_hook(self, limit_from_conf = None):
        # do we need to configure how much of data can be accessed?
        if limit_from_conf:
            max = cherrypy.config.get("plot.max_days")
        else:
            max = 0

        # pull required arguments from request
        obj = _maws_request_param("obj")
        enddate = _maws_request_param("enddate")
        startdate = _maws_request_param("startdate")

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

        cherrypy.request.mawsdata = MAWSDataRequest(
            objects = objects,
            parameter = param,
            location = loc)

# eof
