from decimal import Decimal
from typing import Any, cast, Optional, Dict, Sequence, Set
import unittest

import boto3
from botocore.exceptions import ClientError
from moto import mock_dynamodb2

from pyrazine.auth import DDBAuthStorage
from pyrazine.auth.base import BaseUserProfile
from pyrazine.exceptions import UserNotFoundError


class MockProfile(BaseUserProfile):

    _user_id: str
    _string_field: str
    _integer_field: int
    _float_field: float
    _decimal_field: Decimal
    _roles: Set[str]

    def __init__(self,
                 user_id: str,
                 string_value: str,
                 integer_value: int,
                 float_value: float,
                 decimal_value: Decimal,
                 roles: Sequence[str]):

        self._user_id = user_id
        self._string_field = string_value
        self._integer_field = integer_value
        self._float_field = float_value
        self._decimal_field = decimal_value
        self._roles = set(roles)

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def string_field(self) -> str:
        return self._string_field

    @property
    def integer_field(self) -> int:
        return self._integer_field

    @property
    def float_field(self) -> float:
        return self._float_field

    @property
    def decimal_field(self) -> Decimal:
        return self._decimal_field

    @property
    def roles(self) -> Set[str]:
        return self._roles

    @classmethod
    def from_document(cls, doc: Dict[str, Any]):
        return MockProfile(
            str(doc['userId']),
            str(doc['stringField']),
            int(doc['integerField']),
            float(doc['floatField']),
            Decimal(doc['decimalField']),
            list(doc['roles']),
        )

    def to_document(self) -> Dict[str, Any]:
        return {
            'userId': self._user_id,
            'stringField': self._string_field,
            'integerField': self._integer_field,
            'floatField': self._float_field,
            'decimalField': self._decimal_field,
            'roles': self._roles,
        }

    def __str__(self):
        result = f"userId = {self._user_id}\n"
        result = result + f"stringField = {self._string_field}\n"
        result = result + f"integerField = {self._integer_field}\n"
        result = result + f"floatField = {self._float_field}\n"
        result = result + f"decimalField = {self._decimal_field}\n"
        result = result + f"roles = {self._roles}\n"
        return result


class TestDDBAuthStorage(unittest.TestCase):

    _USER_ID: str = 'user'
    _USER_PROFILE: MockProfile = MockProfile.from_document({
        'userId': _USER_ID,
        'stringField': 'stringValue',
        'integerField': 100,
        'floatField': 2.718,
        'decimalField': Decimal('3.1415'),
        'roles': ['role1', 'role2', 'role3']
    })
    _USER_TABLE = {
        'AttributeDefinitions': [
            {
                'AttributeName': 'userId',
                'AttributeType': 'S',
            }
        ],
        'KeySchema': [
            {
                'AttributeName': 'userId',
                'KeyType': 'HASH',
            }
        ],
    }

    _USER_TABLE_NAME: str = 'user_table'

    def setUp(self) -> None:
        boto3.setup_default_session()

    def _get_auth_storage_object(
            self,
            consistent_read: bool,
            endpoint_url: Optional[str],
            decimal_from_float: bool) -> DDBAuthStorage:

        return DDBAuthStorage(
            self._USER_TABLE_NAME,
            MockProfile,
            consistent_read=consistent_read,
            region_name='us-east-1',
            endpoint_url=endpoint_url,
            decimal_from_float=decimal_from_float,
        )

    def _create_profile_table(self, auth_storage: DDBAuthStorage):
        # Create the profile table.
        auth_storage._ddb_resource.create_table(
            AttributeDefinitions=self._USER_TABLE['AttributeDefinitions'],
            KeySchema=self._USER_TABLE['KeySchema'],
            TableName=self._USER_TABLE_NAME,
        )

    @mock_dynamodb2
    def test_get_user_profile_fails_if_table_not_found(self):
        auth_storage = self._get_auth_storage_object(False, None, True)
        with self.assertRaises(ClientError):
            auth_storage.get_user_profile(self._USER_ID)

    @mock_dynamodb2
    def test_get_user_profile_when_profile_exists(self):
        # Get the auth storage object to test.
        auth_storage = self._get_auth_storage_object(False, None, True)
        self._create_profile_table(auth_storage)

        # Write the user profile to the table.
        auth_storage.put_user_profile(self._USER_ID, self._USER_PROFILE)

        # Fetch the profile from the database.
        response: MockProfile = \
            cast(MockProfile, auth_storage.get_user_profile(self._USER_ID))

        # Make sure the profile fetched matches the one stored.
        self.assertEqual(response.user_id, self._USER_PROFILE.user_id)
        self.assertEqual(response.string_field, self._USER_PROFILE.string_field)
        self.assertEqual(response.integer_field, self._USER_PROFILE.integer_field)
        self.assertEqual(response.float_field, self._USER_PROFILE.float_field)
        self.assertEqual(response.decimal_field, self._USER_PROFILE.decimal_field)
        self.assertEqual(response.roles, self._USER_PROFILE.roles)

    @mock_dynamodb2
    def test_get_user_profile_when_profile_not_exists(self):
        # Get the auth storage object to test.
        auth_storage = self._get_auth_storage_object(False, None, True)
        self._create_profile_table(auth_storage)

        # Assert that a UserNotFoundError is raised if the user ID does not exist in the table.
        with self.assertRaises(UserNotFoundError):
            auth_storage.get_user_profile(self._USER_ID)
