from decimal import Decimal
import logging
from typing import Optional, Set

from pyrazine.exceptions import UserNotFoundError
from pyrazine.auth.base import (
    BaseAuthStorage,
    BaseUserProfile,
)

import boto3
from botocore.exceptions import ClientError


logger = logging.getLogger()


class DDBAuthStorage(BaseAuthStorage):
    """
    This class implements a storage backend for user profiles that uses a DynamoDB table to
    store user information.
    """

    def __init__(self,
                 user_table_name: str,
                 user_profile_cls: BaseUserProfile.__class__,
                 consistent_read: bool = False,
                 region_name: Optional[str] = None,
                 endpoint_url: Optional[str] = None,
                 decimal_from_float: bool = False):
        """
        Creates a new instance of the DDBAuthStorage class.

        :param user_table_name: The name of the DynamoDB table that contains user profiles.
        :param user_profile_cls: The class type that models the user profile, and which will
        be instantiated every time a profile object is created.
        :param consistent_read: Whether the read to the DynamoDB table should be a consistent
        read. Default is False.
        :param endpoint_url: The URL of the DynamoDB endpoint. Mainly for testing purposes.
        Default is None.
        """

        self._consistent_read = consistent_read

        self._ddb_resource = boto3.resource(
            'dynamodb',
            region_name=region_name,
            endpoint_url=endpoint_url,
        )
        self._user_table = self._ddb_resource.Table(user_table_name)
        self._user_class = user_profile_cls
        self._decimal_from_float = decimal_from_float

    def get_user_profile(self, user_id: str):
        """
        Retrieves the whole profile for a given user ID.

        :param user_id: The ID of the user to fetch the profile for.
        :return: A profile object that inherits from BaseUserProfile and exposing a from_document
        method.
        """

        try:
            response = self._user_table.get_item(
                Key={
                    'userId': user_id,
                },
                ConsistentRead=self._consistent_read,
            )
        except ClientError as e:
            logger.exception(e)
            raise
        else:
            if 'Item' not in response:
                raise UserNotFoundError(
                    user_id=user_id,
                    message=f'User {user_id} not found in profile table.'
                )

            return self._user_class.from_document(response['Item'])

    def get_user_roles(self, user_id: str) -> Set[str]:
        """
        Only retrieves the roles assigned to a user. Preferable to retrieving the whole
        profile if just doing RBAC.

        :param user_id: The ID of the user to fetch the roles for.
        :return: A set containing the roles assigned to the user.
        """

        try:
            response = self._user_table.get_item(
                Key={
                    'userId': user_id,
                },
                ConsistentRead=self._consistent_read,
                ProjectionExpression='#roles',
                # The word «roles» is a reserved keyword, so we need to pass it
                # as an expression attribute.
                ExpressionAttributeNames={
                    '#roles': 'roles'
                }
            )
        except ClientError as e:
            logger.exception(e)
            raise
        else:
            if 'Item' not in response:
                raise UserNotFoundError(
                    user_id=user_id,
                    message='User {user_id} not found in profile table.'
                )

            return set(response['Item']['roles']) if 'roles' in response['Item'] else set()

    def put_user_profile(self, user_id: str, user_profile: BaseUserProfile) -> None:
        """
        Updates the user profile.

        :param user_id:
        :param user_profile:
        :return:
        """
        item = user_profile.to_document()
        float_keys = [k for k in item.keys() if isinstance(item[k], float)]
        if len(float_keys) > 0 and not self._decimal_from_float:
            raise ValueError(
                f'Fields {list(float_keys)} is a float, but decimal_to_float is false.')

        # Convert any float values to decimals.
        for key in float_keys:
            item[key] = Decimal(str(item[key]))

        try:
            self._user_table.put_item(
                Item=item,
            )
        except ClientError as e:
            logger.exception(e)
            raise
