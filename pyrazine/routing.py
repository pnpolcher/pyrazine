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
from typing import Any, Callable, ClassVar, Dict, List, Optional, Tuple


AuthorizerCallable = Callable[[], bool]


class Route(object):

    _path: str
    _variable_map: Dict[int, Dict[str, str]]
    _authorizer: AuthorizerCallable
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
    _regex: re.Pattern

    def __init__(self, path: str) -> None:
        self._path = path
        self._regex, self._variable_map = self._compile_regex()

    @staticmethod
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
                regex = regex + f'{segment_type_regex}/'
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

    def match(self, path: str) -> (bool, Optional[Dict[str, Any]]):

        match = self._regex.match(path)
        return False, None \
            if match is None else True, self._parse_variables(match)


class Router(object):

    _routes: List[Route]

    def __init__(self) -> None:
        self._routes = []

    def add_route(self, path: str) -> None:
        self._routes.append(Route(path))

    def route(self, path: str) -> None:
        for route in self._routes:
            matched, variables = route.match(path)
            if matched:


"""

"""