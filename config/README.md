# framework and application configuration

## OpenShift + local execution
OpenShift applications have their configuration exposed through environment variables set by OpenShift. CherryPy configuration files can read these environment values and use them as configuration for the application. This way rest of the application does not need to know anything about OpenShift. Only CherryPy configuration framework is used.

For local development environment:
* Expose database through 'rhc port-forward'
* Set environment variables that are referenced in configuration files
* Execute wsgi.py as normal script through Python3 interpreter (CherryPy native HTTP server is used)

## Other execution environments
Simply hard code wanted values to configuration files directly and you either execute this app as WSGI application or run as standalone application by executing wsgi.py through Python3 interpreter (CherryPy native HTTP server is used).
