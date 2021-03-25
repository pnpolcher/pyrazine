import unittest
from typing import Set

from tests.helpers import get_access_token
from pyrazine.auth import CognitoAuthorizer
from pyrazine.auth.base import BaseAuthStorage, BaseUserProfile
from pyrazine.exceptions import (
    HttpForbiddenError,
)
from pyrazine.jwt import JwtToken


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

        profile = self._authorizer.authorizer([], self._get_access_token())
        self.assertIsInstance(profile, dict)

    def test_auth_wrong_role_one_available(self):

        self._auth_storage.set_mock_roles({'wrong_role'})

        with self.assertRaises(HttpForbiddenError):
            self._authorizer.authorizer(['right_role'], self._get_access_token())

    def test_auth_wrong_role_multiple_required_and_available(self):

        self._auth_storage.set_mock_roles({'right_role_1', 'wrong_role'})

        with self.assertRaises(HttpForbiddenError):
            self._authorizer.authorizer(['right_role_1', 'right_role_2'], self._get_access_token())

    def test_auth_correct_role_when_one_required(self):

        self._auth_storage.set_mock_roles({'right_role'})

        profile = self._authorizer.authorizer(['right_role'], self._get_access_token())
        self.assertIsInstance(profile, dict)

    def test_auth_correct_role_when_multiple_available(self):

        self._auth_storage.set_mock_roles({'required_role', 'another_role'})

        profile = self._authorizer.authorizer(['required_role'], self._get_access_token())
        self.assertIsInstance(profile, dict)

    def test_auth_correct_role_when_multiple_required_and_available(self):

        self._auth_storage.set_mock_roles({'required_role', 'another_role'})

        profile = self._authorizer.authorizer(['required_role', 'another_role'],
                                              self._get_access_token())
        self.assertIsInstance(profile, dict)
