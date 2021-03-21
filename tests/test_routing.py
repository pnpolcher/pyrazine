import itertools
from typing import ClassVar, List, Set
import unittest

from pyrazine.exceptions import MethodNotAllowedError
from pyrazine.response import HttpResponse
from pyrazine.routing import Route, Router


class TestRoute(unittest.TestCase):

    _VALID_METHODS: ClassVar[List[str]] = [
        'GET', 'POST', 'PUT', 'PATCH', 'HEAD', 'OPTIONS', 'DELETE', 'TRACE'
    ]

    @staticmethod
    def _mock_failure_authorizer(roles: Set[str]) -> bool:
        return False

    @staticmethod
    def _mock_success_authorizer(roles: Set[str]) -> bool:
        return True

    @staticmethod
    def _mock_handler():
        return HttpResponse()

    def test_route_methods(self):
        for repeats in range(1, len(TestRoute._VALID_METHODS) + 1):
            for methods in itertools.combinations(TestRoute._VALID_METHODS, repeats):
                _ = Route(methods, '/')

        with self.assertRaises(ValueError):
            Route(['NOMETHOD'], '/')

    def test_route_patterns(self):
        root_route = Route(['GET'], '/')
        self.assertTrue(root_route.match('GET', '/')[0])
        with self.assertRaises(MethodNotAllowedError):
            root_route.match('POST', '/')

        self.assertFalse(root_route.match('GET', '/test')[0])
        self.assertFalse(root_route.match('GET', '/test/')[0])

        simple_long_path = '/submit/sample_path'
        simple_long_route = Route(['POST'], simple_long_path)
        self.assertTrue(simple_long_route.match('POST', simple_long_path)[0])
        self.assertFalse(simple_long_route.match('POST', '/')[0])

        simple_typed_repl_route = Route(['PUT'], '/users/<int:user_id>')
        match, variables = simple_typed_repl_route.match('PUT', '/users/10')
        self.assertTrue(match)
        self.assertEqual(variables.get('user_id', None), 10)

        simple_untyped_repl_route = Route(['PUT'], '/users/<user_id>')
        match, variables = simple_untyped_repl_route.match('PUT', '/users/abc')
        self.assertTrue(match)
        self.assertEqual(variables.get('user_id', None), 'abc')

        complex_typed_repl_route = Route(['PATCH'], '/users/<str:user_id>/<int:page>')
        match, variables = complex_typed_repl_route.match('PATCH', '/users/abc/1')
        self.assertTrue(match)
        self.assertEqual(variables.get('user_id', None), 'abc')
        self.assertEqual(variables.get('page', None), 1)

    def test_router(self):
        router = Router()

        # Add a root route without an authorizer
        router.add_route(['GET', 'POST'], '/', self._mock_handler)

        # Add a route with a simple path with a success authorizer.
        router.add_route(
            ['GET', 'POST'],
            '/submit/success_path',
            self._mock_handler,
            self._mock_success_authorizer)

        # Add a route with a simple path with a failure authorizer.
        router.add_route(
            ['GET', 'POST'],
            '/submit/failure_path',
            self._mock_handler,
            self._mock_failure_authorizer
        )

        # Add a route with a typed path placeholder
        router.add_route(
            ['GET', 'POST'],
            '/users/<int:user_id>',
            self._mock_handler,
            self._mock_success_authorizer
        )
