"""
A lightweight server framework.

To use this module, import the 'application' function, which will dispatch
requests based on handlers. To define a handler, decorate a function with
the 'handler' decorator. Example:

>>> from hanlder import handler, application
... @handler
... def spam():
...     return True
"""

import json
from database import session

handlers = {}

import logging
logger = logging.getLogger("vatic.server")

try:
    from wsgilog import log as wsgilog
except ImportError:
    def wsgilog(*args, **kwargs):
        return lambda x: x

def handler(type = "json", jsonify = None, post = False, environ = False):
    """
    Decorator to bind a function as a handler in the server software.

    type        specifies the Content-Type header
    jsonify     dumps data in json format if true
    environ     gives handler full control of environ if ture
    """
    type = type.lower()
    if type == "json" and jsonify is None:
        jsonify = True
        type == "text/json"
    def decorator(func):
        handlers[func.__name__] = (func, type, jsonify, post, environ)
        return func
    return decorator

@wsgilog(tostream=True)
def application(environ, start_response):
    """
    Dispatches the server application through a handler. Specify a handler
    with the 'handler' decorator.
    """
    path = environ.get("PATH_INFO", "").lstrip("/").split("/")

    logger.info("Got HTTP request: {0}".format("/".join(path)))

    try:
        action = path[0]
    except IndexError:
        raise Error404("Missing action.")

    try:
        handler, type, jsonify, post, passenviron = handlers[action]
    except KeyError:
        start_response("200 OK", [("Content-Type", "text/plain")])
        return ["Error 404\n", "Action {0} undefined.".format(action)]

    try:
        args = path[1:]
        if post:
            postdata = environ["wsgi.input"].read()
            if post == "json":
                args.append(json.loads(postdata))
            else:
                args.append(postdata)
        if passenviron:
            args.append(environ)
        try:
            response = handler(*args)
        finally:
            session.remove()
    except Error404 as e:
        start_response("404 Not Found", [("Content-Type", "text/plain")])
        return ["Error 404\n", str(e)]
    except Error500 as e:
        start_response("500 Internal Serve Error", [("Content-Type", "text/plain")])
        return [str(e)]
    else:
        start_response("200 OK", [("Content-Type", type)])
        if jsonify:
            logger.debug("Response to " + str("/".join(path)) + ": " +
                str(response)[0:100])
            return [json.dumps(response)]
        else:
            return response

class Error404(Exception):
    """
    Exception indicating that an 404 error occured.
    """
    def __init__(self, message):
        Exception.__init__(self, message)

class Error500(Exception):
    """
    Exception indicating that an 404 error occured.
    """
    def __init__(self, message):
        Exception.__init__(self, message)
