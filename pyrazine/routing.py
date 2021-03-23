"""
Routing in Pyrazine is handled by an instance of the Routing class (or any derived class).

Every route needs to be registered using the corresponding `route` attribute, which indicates
the handler that the method following the attribute should be indexed under the route pattern
passed.

Internally, the handler will instantiate a `Route` object with the path pattern. `Route` parses
the path and builds a regex that matches only compliant paths. Then, the router stores the route
internally.
"""

import re
from typing import Any, Callable, ClassVar, Dict, List, Optional, Set, Tuple, Union

from pyrazine.context import RequestContext
from pyrazine.exceptions import (
    HttpNotFoundError,
    MethodNotAllowedError,
    HttpForbiddenError,
)
from pyrazine.jwt import JwtToken
from pyrazine.response import HttpResponse


AuthorizerCallable = Callable[[List[str], JwtToken, Optional[Dict[str, Any]]], bool]
HandlerCallable = Callable[[JwtToken, Dict[str, Any], RequestContext], HttpResponse]


class Route(object):

    _methods: List[str]
    _path: str
    _variable_map: Dict[int, Dict[str, str]]
    _authorizer: Optional[AuthorizerCallable]
    _auth_context: Optional[Dict[str, Any]]
    _handler: HandlerCallable
    _REGEX_BY_TYPE: ClassVar[Dict[str, str]] = {
        'int': '\\d+',
        'float': '[+-]([0-9]*[.])?[0-9]+',
        'str': '[A-Za-z0-9-._~:/?#\\[\\]@!$&\'()*+,;%=]+',
    }
    _CONVERTER_BY_TYPE: ClassVar[Dict[str, Any]] = {
        'int': int,
        'float': float,
        'str': str,
    }
    _VALID_HTTP_METHODS = {'GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD', 'PATCH', 'TRACE'}
    _regex: re.Pattern
    _roles: List[str]

    def __init__(self,
                 methods: Union[List[str], Tuple[str]],
                 path: str,
                 roles: Optional[Union[List[str], Tuple[str]]] = None) -> None:
        """
        Constructs a new instance of the Route class, containing the methods by which this
        endpoint can be invoked, together with a path pattern that needs to match in order to
        invoke the handler for this endpoint.

        :param methods: The methods that can be used to invoke this endpoint.
        :param path: The path pattern that needs to be matched in order to invoke this
        endpoint.
        :param roles: The roles that a user needs in order to successfully invoke this endpoint, if
        authorization is present. Defaults to None.
        """

        self._methods = list([m.upper() for m in methods])
        if not set(self._methods).issubset(Route._VALID_HTTP_METHODS):
            invalid_methods = set(self._methods).difference(Route._VALID_HTTP_METHODS)
            raise ValueError(f'The following methods are invalid: {invalid_methods}')

        self._path = path
        self._regex, self._variable_map = self._compile_regex()
        self._roles = list(roles) if roles is not None else list()
        self._authorizer = None
        self._auth_context = {}

    @property
    def authorizer(self) -> Optional[AuthorizerCallable]:
        return self._authorizer

    @authorizer.setter
    def authorizer(self, handler: Optional[AuthorizerCallable]) -> None:
        self._authorizer = handler

    @property
    def auth_context(self) -> Dict[str, Any]:
        return self._auth_context

    @auth_context.setter
    def auth_context(self, ctx: Optional[Dict[str, Any]]):
        self._auth_context = ctx or {}

    @property
    def handler(self) -> HandlerCallable:
        return self._handler

    @handler.setter
    def handler(self, h: HandlerCallable) -> None:
        self._handler = h

    @property
    def roles(self) -> List[str]:
        return self._roles

    def _compile_regex(self) -> Tuple[re.Pattern, Dict[int, Dict[str, str]]]:
        """
        Takes a path and produces a regex that matches against the path, extracting all
        variables as groups.

        :return: A tuple containing the compiled regex, and a dictionary mapping variable
        names to types and match groups.
        """

        # Next regex group to be assigned to a variable.
        current_group = 1

        variable_map: Dict[int, Dict[str, str]] = {}

        # Split the path into multiple segments.
        # TODO: Expand regex to cover all valid characters.
        segments = re.findall('/(?=([A-Za-z0-9_<>:]+))', self._path)
        regex = '^/'

        # Iterate through all captured segments.
        for segment in segments:

            # Parse the current segment.
            parsed_segment = re.match('^<(?:([A-Za-z0-9_]+):)?([A-Za-z0-9_]+)>$', segment)

            # If the regex matched and we captured two groups, it's a variable segment.
            if parsed_segment is not None and parsed_segment.lastindex == 2:

                # Get the corresponding regex for the this type of segment. Default type
                # is str.
                segment_type = parsed_segment[1]
                segment_type_regex = Route._REGEX_BY_TYPE[segment_type] \
                    if parsed_segment[1] is not None \
                    and parsed_segment[1].lower() in Route._REGEX_BY_TYPE \
                    else Route._REGEX_BY_TYPE['str']

                # Get the variable name.
                variable_name = parsed_segment[2]

                # Add the regex for this segment to the path regex and add the
                # variable to the variable map.
                regex = regex + f'({segment_type_regex})/'
                variable_map[current_group] = {
                    'variable_name': variable_name,
                    'variable_type': segment_type
                }
                current_group = current_group + 1
            else:
                # Segment is a constant.
                regex = regex + f'{segment}/'

        regex = regex + '$'
        return re.compile(regex), variable_map

    def _parse_variables(self, match: re.Match) -> Dict[str, Any]:
        variables = {}
        for group_n, var_data in self._variable_map.items():
            var_name = var_data['variable_name']
            var_type = var_data['variable_type']

            converter = Route._CONVERTER_BY_TYPE.get(var_type, None) or str
            var_value = converter(match[group_n])
            variables[var_name] = var_value

        return variables

    def match(self, method: str, path: str) -> (bool, Optional[Dict[str, Any]]):
        """
        Tests whether a given set of method and path match this route.

        :param method: The method with which an endpoint was invoked.
        :param path: The path that points to the endpoint.
        :return: A tuple, whose first element is True if both method and path matched,
        and whose second element contains a dictionary of path variables matched, if any.
        Otherwise, the variable dictionary is an empty dictionary.
        """

        # Make sure there is a trailing forward slash before matching.
        if not path.endswith('/'):
            path = f'{path}/'

        # Test if the regex matches the path.
        match = self._regex.match(path)

        # If it doesn't, we can safely return False and try the next route.
        if match is None:
            return False, None
        elif method.upper() not in self._methods:
            # If the path matches, but the method is not in the allowed method list, then
            # throw a MethodNotAllowedError exception, i.e.: we found the handler, but the
            # method was not allowed.
            raise MethodNotAllowedError(method, 'Method not allowed')

        # Both method and path match, so parse the URL variables and return True.
        return True, self._parse_variables(match)


class Router(object):

    _routes: List[Route]

    def __init__(self) -> None:
        self._routes = []

    def add_route(self,
                  methods: Union[List[str], Tuple[str]],
                  path: str,
                  handler: HandlerCallable,
                  authorizer: Optional[AuthorizerCallable] = None,
                  auth_context: Optional[Dict[str, Any]] = None,
                  roles: Optional[Union[List[str], Tuple[str]]] = None) -> None:
        """
        Adds a route to the routing table.

        :param methods: The allowed methods for this route.
        :param path: The path expression to match.
        :param handler: The handler used to process calls to this endpoint.
        :param authorizer: The authorizer that tests whether the user is authorized to
        invoke this endpoint.
        :param auth_context:A dictionary containing context information for the authorizer.
        Default is False.
        :param roles: The roles that a user needs to successfully invoke this route, if
        authorization is enabled. Defaults to
        None.
        :return: None.
        """

        route = Route(methods, path, roles)
        route.handler = handler
        route.authorizer = authorizer
        route.auth_context = auth_context

        self._routes.append(route)

    def route(self,
              method: str,
              path: str,
              token: JwtToken,
              body: Dict[str, Any],
              ctx: RequestContext) -> HttpResponse:
        """
        Route the request to the right handler.

        :param method: The HTTP method with which the endpoint was invoked.
        :param path: The path to the endpoint.
        :param token: The JWT token passed to the endpoint, if any.
        :param body: The contents of the HTTP request body.
        :param ctx: The local context of the request.
        :return: A HttpResponse object with the result of the operation.
        """

        response = None
        for route in self._routes:
            matched, variables = route.match(method, path)

            # If the route matches, run the authorizer, if any is assigned to this route.
            if matched:
                # If the method needs authorization, run the authorizer. If the user is not
                # authorized to invoke the endpoint, the authorizer should throw a ForbiddenError
                # exception.
                if route.authorizer is not None:
                    profile = route.authorizer(route.roles, token, route.auth_context)
                else:
                    profile = None

                # Authorization passed, so run the handler.
                ctx = ctx.copy(path_variables=variables, profile=profile)

                response = route.handler(token, body, ctx)

        # If no endpoint matched, raise an exception for a HTTP 404 Not Found error.
        if response is None:
            raise HttpNotFoundError()

        return response
