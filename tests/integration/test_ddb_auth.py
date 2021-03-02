import json
import os
import time
import unittest

import boto3
from botocore import UNSIGNED
from botocore.config import Config
from jose import jwt
import pytest


class DDBAuthTest(unittest.TestCase):

    LOCAL_LAMBDA_ENDPOINT='http://localhost:9001/'
    LAMBDA_FUNCTION_NAME='test_lambda'

    JWT_SECRET = 'pyrazine'
    CLAIMS = {
        'sub': 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
        'aud': '',
        'iss': 'https://cognito-idp.us-east-1.amazonaws.com/us-east-1_example',
        'exp': int(time.time()) + 86400,
    }

    def setUp(self) -> None:
        self._lambda_client = boto3.client(
            'lambda',
            endpoint_url=self.LOCAL_LAMBDA_ENDPOINT,
            use_ssl=False,
            verify=False,
            region_name='eu-west-1',
            config=Config(
                signature_version=UNSIGNED,
                retries={
                    'max_attempts': 0
                }
            )
        )

    def _generate_jwt(self) -> str:
        token = jwt.encode(self.CLAIMS, self.JWT_SECRET, algorithm='HS256')
        return token

    def _get_event(self, method: str, path: str, inject_jwt: bool = False) -> str:
        path_to_json = os.path.join(os.getcwd(), f'test_{method}.json')
        with open(path_to_json, 'r') as f:
            json_object = json.load(f)

        json_object['requestContext']['http']['path'] = path

        if inject_jwt:
            jwt_token = self._generate_jwt()
            json_object['requestContext']['authorizer']['jwt']['claims'] = self.CLAIMS
            json_object['headers']['authorization'] = f"Bearer {jwt_token}"
        else:
            del json_object['requestContext']['authorizer']

        return json.dumps(json_object)

    @pytest.mark.integration
    def test_authreq_get_authorized(self):
        response = self._lambda_client.invoke(
            FunctionName=self.LAMBDA_FUNCTION_NAME,
            Payload=self._get_event('get', '/auth', inject_jwt=True),
        )

    @pytest.mark.integration
    def test_authreq_get_unauthorized(self):
        response = self._lambda_client.invoke(
            FunctionName=self.LAMBDA_FUNCTION_NAME,
            Payload=self._get_event('get', '/auth')
        )
