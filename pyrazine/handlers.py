import functools
import json
import logging
import os
from typing import Callable, Dict, List, Tuple, Union

from pyrazine.events import HttpEvent
from pyrazine.jwt import JwtToken
from pyrazine.response import HttpResponse
from pyrazine.tracer import Tracer
from pyrazine.typing import LambdaContext

import aws_xray_sdk.core


is_cold_start = True

HandlerCallable = Callable[[JwtToken, Dict[str, object]], HttpResponse]

ENVIRONMENT = os.environ.get('ENVIRONMENT') or 'DEV'

logger = logging.getLogger(__name__)
logger_level = logging.DEBUG if ENVIRONMENT == 'DEV' else logging.INFO
logger.setLevel(logger_level)


class LambdaHandler(object):

    def __init__(self,
                 service_name: str = 'unknown_service',
                 recorder: aws_xray_sdk.core.xray_recorder = None,
                 trace: bool = True):
        self._allowed_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
        self._routes = {}

        self._service_name = service_name
        self._trace = trace
        self._tracer = Tracer(recorder=recorder)

        if self._trace:
            logging.debug('Patching modules for instrumentation.')
            aws_xray_sdk.core.patch_all()

    @staticmethod
    def _get_body_object(http_event: HttpEvent) -> Tuple[bool, Dict[str, object]]:

        # It's okay to have a «bodyless» request, maybe the endpoint does not
        # require any data. Just make sure to return an empty object.
        if http_event.body is None:
            return True, {}

        # If there is actually something, let's make sure it's valid data.
        # Only JSON is supported at the moment.
        try:
            result = json.loads(http_event.body)
            success = True
        except json.decoder.JSONDecodeError:
            result = HttpResponse.build_error_response(400, message='Malformed JSON input')
            success = False

        return success, result

    def _handle_event(self, event: HttpEvent, path: str) -> Dict[str, object]:

        method = event.http_ctx_method.upper()
        logger.debug(f'Processing {method} route for path {path}')

        if method == 'OPTIONS':
            return HttpResponse.build_success_response()

        success, body = self._get_body_object(event)
        if success:
            method_routes = self._routes.get(method)
            if method_routes is None:
                error_msg = f'No routes found for method {method}'
                logger.error(error_msg)
                raise KeyError(error_msg)

            handler = method_routes.get(path)
            if handler is None:
                error_msg = f'No handler defined for method {method} and path {path}'
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            response = handler(event.jwt, body)
        else:
            response = HttpResponse.build_error_response(404, message='Not found.')

        return response

    @functools.lru_cache
    def _tracer_wrap_handler(self,
                             handler: HandlerCallable,
                             persist_response: bool = False) -> HandlerCallable:
        """
        Wraps a function handler with tracing code.

        A functools LRU cache with default maximum size is used to cache the
        wrapped functions and avoid creating unnecessary objects.

        :param handler:
        :return:
        """

        handler_name = handler.__name__

        @functools.wraps(handler)
        def wrapper(token: JwtToken, body: Dict[str, object]) -> HttpResponse:
            logger.debug("Tracing handler executed")
            with self._tracer.in_subsegment(name=f"## {handler_name}") as subsegment:
                global is_cold_start

                if is_cold_start:
                    subsegment.put_annotation(key='ColdStart', value=True)
                    is_cold_start = False

                try:
                    logger.debug(f'Starting handler {handler_name}')
                    response = handler(token, body)
                    logger.debug(f'Returned successfully from handler {handler_name}')

                    self._tracer.trace_route(
                        handler_name=handler_name,
                        persist_response=persist_response,
                        response_data=response,
                        subsegment=subsegment
                    )
                except Exception as err:
                    logger.exception(f'Handler {handler_name} raised an exception.')
                    self._tracer.trace_exception(
                        handler_name=handler_name,
                        exception=err,
                        subsegment=subsegment)
                    raise

            return response

        return wrapper

    def _add_route(self,
                   method: str,
                   path: str,
                   handler: HandlerCallable,
                   trace: bool = None,
                   persist_response: bool = False) -> None:

        if method not in self._allowed_methods:
            raise ValueError("Method {0} not among the allowed methods.".format(method))

        # Wrap handler with tracer, if tracing is enabled.
        if trace or (trace is None and self._trace):
            logger.debug(f"Tracer enabled for {method} {path}")
            handler = self._tracer_wrap_handler(
                handler,
                persist_response=persist_response)

        if method not in self._routes:
            routes_by_method = {}
            self._routes[method] = routes_by_method
        else:
            routes_by_method = self._routes[method]

        routes_by_method[path] = handler

    def route(self,
              handler: HandlerCallable = None,
              path: str = None,
              methods: Union[List[str], Tuple[str]] = None,
              trace: bool = None,
              persist_response: bool = False):
        """
        Registers a function as a handler for a given combination of method and
        path.

        :param handler: The function to use for a given combination of method and
        path.
        :param path: The path to the resource.
        :param methods: The methods that the resource accepts.
        :param trace: True, if calls to this function should be traced.
        :param persist_response: True, if traces should be persisted as metadata
        within a trace subsegment.
        :return:
        """

        if handler is None:
            return functools.partial(self.route, path=path, methods=methods)

        if methods is None:
            methods = ['GET']
        elif not isinstance(methods, list) and not isinstance(methods, tuple):
            raise TypeError('Allowed methods should be a list or tuple of strings.')

        for method in methods:
            self._add_route(method.upper(), path, handler,
                            trace=trace, persist_response=persist_response)

        return handler

    def handle_request(
            self,
            event: Dict[str, object],
            context: LambdaContext) -> Dict[str, object]:
        """
        Invokes the corresponding route handler for the event and context objects
        passed and returns a dictionary of objects indexed by strings, compatible
        with a Lambda response object.

        If there is no route handler to process the request, an object populated
        with an appropriate message and an HTTP 400 status code (Bad Request) is
        returned.

        :param event: The event object passed by AWS Lambda.
        :param context: The context object passed by AWS Lambda.
        :return: A response object, as expected by AWS Lambda.
        """

        http_event = HttpEvent(event)
        method = http_event.http_ctx_method
        path = http_event.path

        if method is None or path is None:
            method_present = 'not' if method is None else ''
            path_present = 'not' if path is None else ''

            logger.error(
                f"Method {method_present} present, path {path_present} present.")
            response = HttpResponse.build_error_response(400, message='Bad request')
        elif method in self._allowed_methods:
            response = self._handle_event(http_event, path)
        else:
            response = HttpResponse.build_error_response(405, message='Method not allowed')

        return response.get_response_object()
