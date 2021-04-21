import functools
import json
import logging
import os
from typing import Any, Dict, Optional, Sequence

from pyrazine.auth.base import BaseAuthorizer
from pyrazine.context import RequestContext
from pyrazine.errorhandling import BaseErrorHandler, DefaultErrorHandler
from pyrazine.events import HttpEvent
from pyrazine.exceptions import BadRequestError
from pyrazine.jwt import JwtToken
from pyrazine.response import HttpResponse
from pyrazine.routing import Router, HandlerCallable
from pyrazine.tracer import Tracer
from pyrazine.typing import LambdaContext

import aws_xray_sdk.core


is_cold_start = True

ENVIRONMENT = os.environ.get('ENVIRONMENT') or 'DEV'

logger = logging.getLogger(__name__)
logger_level = logging.DEBUG if ENVIRONMENT == 'DEV' else logging.INFO
logger.setLevel(logger_level)


class ApiGatewayEventHandler(object):

    _error_handler: BaseErrorHandler
    _router: Router

    def __init__(self,
                 service_name: str = 'unknown_service',
                 authorizer: Any = None,
                 error_handler: Optional[BaseErrorHandler] = None,
                 recorder: aws_xray_sdk.core.xray_recorder = None,
                 trace: bool = True):
        """
        Constructs a new instance of the LambdaHandler class, which is responsible for handling
        AWS Lambda events passed to the Lambda function.

        :param service_name: THe name of the service provided by the AWS Lambda function.
        :param authorizer: Optional argument to pass an authorizer. Currently supported are
        authorizers derived of the BaseAuthorizer class. Defaults to None.
        :param error_handler: Optional argument to pass a custom error handler. Must implement
        BaseErrorHandler. Defaults to None. Passing None as the error handler instructs the
        constructor to create an instance of the DefaultErrorHandler class.
        :param recorder: An AWS X-Ray recorder instance. Defaults to None.
        :param trace: Whether AWS X-Ray tracing should be enabled for this Lambda function.
        """

        self._error_handler = error_handler or DefaultErrorHandler()
        self._router = Router()

        self._authorizer = authorizer
        self._service_name = service_name
        self._trace = trace
        self._tracer = Tracer(recorder=recorder)

        if self._trace:
            logging.debug('Patching modules for instrumentation.')
            aws_xray_sdk.core.patch_all()

    @property
    def authorizer(self):
        return self._authorizer

    @staticmethod
    def _get_body_object(http_event: HttpEvent) -> Dict[str, object]:

        # TODO: Handle binary payloads.

        # It's okay to have a «bodyless» request, maybe the endpoint does not
        # require any data. Just make sure to return an empty object.
        if http_event.body is None:
            return {}

        # If there is actually something, let's make sure it's valid data.
        # Only JSON is supported at the moment.
        try:
            result = json.loads(http_event.body)
        except json.decoder.JSONDecodeError:
            raise BadRequestError('Malformed JSON input')

        return result

    def _handle_event(self, event: HttpEvent, path: str) -> HttpResponse:

        method = event.http_ctx_method.upper()
        logger.debug(f'Handling event for route at {method} {path}.')

        # TODO: Better support for OPTIONS.
        if method == 'OPTIONS':
            return HttpResponse.build_success_response()

        try:
            body = self._get_body_object(event)
            context = RequestContext(
                cookies=event.cookies,
                headers=event.headers,
                query_string=event.query_string,
            )
            response = self._router.route(method, path, event.jwt, body, context)
        except Exception as e:
            logger.exception(e)
            response = self._error_handler.get_response(e, {})

        logger.debug('Event handled.')
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
        def wrapper(
                token: JwtToken,
                body: Dict[str, object],
                context: RequestContext) -> HttpResponse:

            logger.debug("Tracing handler executed")
            with self._tracer.in_subsegment(name=f"## {handler_name}") as subsegment:
                global is_cold_start

                if is_cold_start:
                    subsegment.put_annotation(key='ColdStart', value=True)
                    is_cold_start = False

                try:
                    logger.debug(f'Starting handler {handler_name}')
                    response = handler(token, body, context)
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

    def route(self,
              handler: HandlerCallable = None,
              path: str = None,
              methods: Sequence[str] = None,
              trace: bool = None,
              authorization: bool = False,
              auth_context: Optional[Dict[str, Any]] = None,
              roles: Sequence[str] = (),
              persist_response: bool = False):
        """
        Registers a function as a handler for a given combination of method and
        path.

        :param handler: The function to use for a given combination of method and
        path.
        :param path: The path to the resource.
        :param methods: The methods that the resource accepts.
        :param trace: True, if calls to this function should be traced.
        :param authorization: If True, this method requires that a user is authorized
        to invoke it. Default is False.
        :param auth_context: A dictionary containing context information for the authorizer.
        Default is False.
        :param roles: If this method requires authorization, this is a list of the roles
        that a user needs to be allowed to invoke it. Default is an empty list.
        :param persist_response: True, if traces should be persisted as metadata
        within a trace subsegment.
        :return:
        """

        logger.debug(f'Setting up route with methods {methods} for path {path}.')

        if handler is None:
            return functools.partial(self.route,
                                     path=path,
                                     methods=methods,
                                     trace=trace,
                                     authorization=authorization,
                                     auth_context=auth_context,
                                     roles=roles,
                                     persist_response=persist_response)

        if methods is None:
            methods = ('GET', )
        elif not isinstance(methods, list) and not isinstance(methods, tuple):
            raise TypeError('Allowed methods should be a list or tuple of strings.')

        # Wrap handler with tracer, if tracing is enabled.
        if trace or (trace is None and self._trace):
            handler = self._tracer_wrap_handler(
                handler,
                persist_response=persist_response)

        if authorization and isinstance(self._authorizer, BaseAuthorizer):
            authorizer = self._authorizer.authorizer
        else:
            authorizer = None

        self._router.add_route(methods, path, handler, authorizer, auth_context, roles)

        logger.debug('Route set up successfully.')

        return handler

    def handle_request(
            self,
            event: Dict[str, object],
            context: LambdaContext) -> Dict[str, Any]:
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

        # If either method or path have not been sent in the event, do not assume
        # anything and just fail with a HTTP 400 code.
        if method is None or path is None:
            method_present = 'not' if method is None else ''
            path_present = 'not' if path is None else ''

            logger.error(
                f"Method {method_present} present, path {path_present} present.")
            response = HttpResponse.build_error_response(400, message='Bad request')
        else:
            response = self._handle_event(http_event, path)

        return response.get_response_object()
