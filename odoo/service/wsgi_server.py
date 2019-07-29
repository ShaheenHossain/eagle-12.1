# -*- coding: utf-8 -*-
# Part of Eagle ERP. See LICENSE file for full copyright and licensing details.

"""

WSGI stack, common code.

"""

import logging
import sys
import threading
import traceback


try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    # pylint: disable=bad-python3-import
    import xmlrpclib

import werkzeug.exceptions
import werkzeug.wrappers
import werkzeug.serving
import werkzeug.contrib.fixers

import eagle
from eagle.tools import config

_logger = logging.getLogger(__name__)

# XML-RPC fault codes. Some care must be taken when changing these: the
# constants are also defined client-side and must remain in sync.
# User code must use the exceptions defined in ``eagle.exceptions`` (not
# create directly ``xmlrpclib.Fault`` objects).
RPC_FAULT_CODE_CLIENT_ERROR = 1 # indistinguishable from app. error.
RPC_FAULT_CODE_APPLICATION_ERROR = 1
RPC_FAULT_CODE_WARNING = 2
RPC_FAULT_CODE_ACCESS_DENIED = 3
RPC_FAULT_CODE_ACCESS_ERROR = 4

def xmlrpc_handle_exception_int(e):
    if isinstance(e, eagle.exceptions.UserError):
        fault = xmlrpclib.Fault(RPC_FAULT_CODE_WARNING, eagle.tools.ustr(e.name))
    elif isinstance(e, eagle.exceptions.RedirectWarning):
        fault = xmlrpclib.Fault(RPC_FAULT_CODE_WARNING, str(e))
    elif isinstance(e, eagle.exceptions.MissingError):
        fault = xmlrpclib.Fault(RPC_FAULT_CODE_WARNING, str(e))
    elif isinstance (e, eagle.exceptions.AccessError):
        fault = xmlrpclib.Fault(RPC_FAULT_CODE_ACCESS_ERROR, str(e))
    elif isinstance(e, eagle.exceptions.AccessDenied):
        fault = xmlrpclib.Fault(RPC_FAULT_CODE_ACCESS_DENIED, str(e))
    elif isinstance(e, eagle.exceptions.DeferredException):
        info = e.traceback
        # Which one is the best ?
        formatted_info = "".join(traceback.format_exception(*info))
        #formatted_info = eagle.tools.exception_to_unicode(e) + '\n' + info
        fault = xmlrpclib.Fault(RPC_FAULT_CODE_APPLICATION_ERROR, formatted_info)
    else:
        info = sys.exc_info()
        # Which one is the best ?
        formatted_info = "".join(traceback.format_exception(*info))
        #formatted_info = eagle.tools.exception_to_unicode(e) + '\n' + info
        fault = xmlrpclib.Fault(RPC_FAULT_CODE_APPLICATION_ERROR, formatted_info)

    return xmlrpclib.dumps(fault, allow_none=None)

def xmlrpc_handle_exception_string(e):
    if isinstance(e, eagle.exceptions.UserError):
        fault = xmlrpclib.Fault('warning -- %s\n\n%s' % (e.name, e.value), '')
    elif isinstance(e, eagle.exceptions.RedirectWarning):
        fault = xmlrpclib.Fault('warning -- Warning\n\n' + str(e), '')
    elif isinstance(e, eagle.exceptions.MissingError):
        fault = xmlrpclib.Fault('warning -- MissingError\n\n' + str(e), '')
    elif isinstance(e, eagle.exceptions.AccessError):
        fault = xmlrpclib.Fault('warning -- AccessError\n\n' + str(e), '')
    elif isinstance(e, eagle.exceptions.AccessDenied):
        fault = xmlrpclib.Fault('AccessDenied', str(e))
    elif isinstance(e, eagle.exceptions.DeferredException):
        info = e.traceback
        formatted_info = "".join(traceback.format_exception(*info))
        fault = xmlrpclib.Fault(eagle.tools.ustr(e), formatted_info)
    #InternalError
    else:
        info = sys.exc_info()
        formatted_info = "".join(traceback.format_exception(*info))
        fault = xmlrpclib.Fault(eagle.tools.exception_to_unicode(e), formatted_info)

    return xmlrpclib.dumps(fault, allow_none=None, encoding=None)

def _patch_xmlrpc_marshaller():
    # By default, in xmlrpc, bytes are converted to xmlrpclib.Binary object.
    # Historically, eagle is sending binary as base64 string.
    # In python 3, base64.b64{de,en}code() methods now works on bytes.
    # Convert them to str to have a consistent behavior between python 2 and python 3.
    # TODO? Create a `/xmlrpc/3` route prefix that respect the standard and uses xmlrpclib.Binary.
    def dump_bytes(marshaller, value, write):
        marshaller.dump_unicode(eagle.tools.ustr(value), write)

    xmlrpclib.Marshaller.dispatch[bytes] = dump_bytes

def application_unproxied(environ, start_response):
    """ WSGI entry point."""
    # cleanup db/uid trackers - they're set at HTTP dispatch in
    # web.session.OpenERPSession.send() and at RPC dispatch in
    # eagle.service.web_services.objects_proxy.dispatch().
    # /!\ The cleanup cannot be done at the end of this `application`
    # method because werkzeug still produces relevant logging afterwards
    if hasattr(threading.current_thread(), 'uid'):
        del threading.current_thread().uid
    if hasattr(threading.current_thread(), 'dbname'):
        del threading.current_thread().dbname
    if hasattr(threading.current_thread(), 'url'):
        del threading.current_thread().url

    with eagle.api.Environment.manage():
        result = eagle.http.root(environ, start_response)
        if result is not None:
            return result

    # We never returned from the loop.
    return werkzeug.exceptions.NotFound("No handler found.\n")(environ, start_response)

def application(environ, start_response):
    if config['proxy_mode'] and 'HTTP_X_FORWARDED_HOST' in environ:
        return werkzeug.contrib.fixers.ProxyFix(application_unproxied)(environ, start_response)
    else:
        return application_unproxied(environ, start_response)