from functools import partial
import itertools
from typing import Any, ClassVar, Dict, List, Optional
import unittest

from pyrazine.exceptions import MethodNotAllowedError
from pyrazine.requests import HttpRequest
from pyrazine.response import HttpResponse
from pyrazine.routing import Route, Router
from pyrazine.jwt import JwtToken
from tests.helpers import get_access_token


class TestRoute(unittest.TestCase):

    _VALID_METHODS: ClassVar[List[str]] = [
        'GET', 'POST', 'PUT', 'PATCH', 'HEAD', 'OPTIONS', 'DELETE', 'TRACE'
    ]

    @staticmethod
    def _mock_failure_authorizer(roles: List[str], token: JwtToken, context: Optional[Dict[str, Any]]) -> bool:
        return False

    @staticmethod
    def _mock_success_authorizer(roles: List[str], token: JwtToken, context: Optional[Dict[str, Any]]) -> bool:
        return True

    @staticmethod
    def _mock_handler(request: HttpRequest, return_value: int) -> HttpResponse:
        return HttpResponse(200, {'return_value': return_value})

    def test_route_methods(self):
        for repeats in range(1, len(TestRoute._VALID_METHODS) + 1):
            for methods in itertools.combinations(TestRoute._VALID_METHODS, repeats):
                Route('/').add_handler(methods, self._mock_handler)

        with self.assertRaises(ValueError):
            Route('/').add_handler(['NOMETHOD'], self._mock_handler)

    def test_route_patterns(self):
        root_route = Route('/')
        root_route.add_handler(['GET'], self._mock_handler)
        self.assertTrue(root_route.match('GET', '/')[0])
        with self.assertRaises(MethodNotAllowedError):
            root_route.match('POST', '/')

        self.assertFalse(root_route.match('GET', '/test')[0])
        self.assertFalse(root_route.match('GET', '/test/')[0])

        simple_long_path = '/submit/sample_path'
        simple_long_route = Route(simple_long_path)
        simple_long_route.add_handler(['POST'], self._mock_handler)
        self.assertTrue(simple_long_route.match('POST', simple_long_path)[0])
        self.assertFalse(simple_long_route.match('POST', '/')[0])

        simple_typed_repl_route = Route('/users/<int:user_id>')
        simple_typed_repl_route.add_handler(['PUT'], self._mock_handler)
        match, variables = simple_typed_repl_route.match('PUT', '/users/10')
        self.assertTrue(match)
        self.assertEqual(variables.get('user_id', None), 10)

        simple_untyped_repl_route = Route('/users/<user_id>')
        simple_untyped_repl_route.add_handler(['PUT'], self._mock_handler)
        match, variables = simple_untyped_repl_route.match('PUT', '/users/abc')
        self.assertTrue(match)
        self.assertEqual(variables.get('user_id', None), 'abc')

        complex_typed_repl_route = Route('/users/<str:user_id>/<int:page>')
        complex_typed_repl_route.add_handler(['PATCH'], self._mock_handler)
        match, variables = complex_typed_repl_route.match('PATCH', '/users/abc/1')
        self.assertTrue(match)
        self.assertEqual(variables.get('user_id', None), 'abc')
        self.assertEqual(variables.get('page', None), 1)

    def test_router(self):
        router = Router()

        # Add a root route without an authorizer
        router.add_route(['GET', 'POST'], '/', partial(self._mock_handler, return_value=-1))

        # Add a route with a simple path with a success authorizer.
        router.add_route(
            ['GET', 'POST'],
            '/submit/success_path',
            partial(self._mock_handler, return_value=0),
            self._mock_success_authorizer)

        # Add a route with a simple path with a failure authorizer.
        router.add_route(
            ['GET', 'POST'],
            '/submit/failure_path',
            partial(self._mock_handler, return_value=1),
            self._mock_failure_authorizer
        )

        # Add a route with a typed path placeholder
        router.add_route(
            ['GET', 'POST'],
            '/users/<int:user_id>',
            partial(self._mock_handler, return_value=2),
            self._mock_success_authorizer
        )

        # Add a route to the users endpoint, but without a placeholder, to test
        # whether the pattern matching is working correctly.
        router.add_route(
            ['GET', 'POST'],
            '/users',
            partial(self._mock_handler, return_value=3),
            self._mock_success_authorizer
        )

        request = HttpRequest({}, jwt_token=get_access_token())

        response = router.route('GET', '/users', request)
        self.assertEqual(response._body['return_value'], 3)

        response = router.route('GET', '/users/1', request)
        self.assertEqual(response._body['return_value'], 2)

    def test_router_two_handlers_two_methods(self):

        router = Router()

        # Add two handlers pointing to the same path with different methods.
        router.add_route(['GET'], '/', partial(self._mock_handler, return_value=-1))
        router.add_route(['POST'], '/', partial(self._mock_handler, return_value=1))

        request = HttpRequest({}, jwt_token=get_access_token())

        response = router.route('POST', '/', request)
        self.assertEqual(response._body['return_value'], 1)
        response = router.route('GET', '/', request)
        self.assertEqual(response._body['return_value'], -1)
