import unittest
from typing import Dict, Set

from tests.helpers import get_access_token
from pyrazine.auth import CognitoAuthorizer
from pyrazine.auth.base import BaseAuthStorage, BaseUserProfile
from pyrazine.jwt import JwtToken
from pyrazine.response import HttpResponse


class MockAuthStorage(BaseAuthStorage):

    _roles: Set[str] = {}

    def set_mock_roles(self, roles: Set[str]):
        self._roles = roles

    def get_user_profile(self, user_id: str) -> BaseUserProfile:
        pass

    def get_user_roles(self, user_id: str) -> Set[str]:
        return self._roles

    def put_user_profile(self, user_id: str, user_profile: BaseUserProfile) -> None:
        pass


class TestCognitoAuthorizer(unittest.TestCase):

    def setUp(self) -> None:

        self._auth_storage = MockAuthStorage()

        self._authorizer = CognitoAuthorizer(
            'user_pool_id',
            'client_id',
            'eu-west-1',
            self._auth_storage,
            False,
        )

    @staticmethod
    def _get_access_token() -> JwtToken:
        claims, token = get_access_token()
        token_object = JwtToken(claims)
        token_object.raw_token = token
        return token_object

    def test_auth_no_roles(self):

        self._auth_storage.set_mock_roles(set())

        @self._authorizer.auth
        def handler_pass(token, body, context) -> HttpResponse:
            self.assertIn('profile', context)
            self.assertEqual(context['profile'], None)
            return HttpResponse()

        handler_pass(self._get_access_token(), {}, {})

    def test_auth_wrong_role(self):
        pass

    def test_auth_correct_role(self):
        pass
