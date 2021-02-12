import json
import os
import urllib


from pyrazine.auth.base import BaseAuthorizer
from pyrazine.jwt import JwtToken


class CognitoAuthorizer(BaseAuthorizer):
    def __init__(self, user_pool_id: str, region: str):
        self._user_pool_id = user_pool_id if user_pool_id is not None else \
            os.environ.get('COGNITO_USER_POOL')
        self._region = region if region is not None else os.environ.get('COGNITO_REGION')

        self._initialize()

    def _initialize(self):
        keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json' \
            . format(self._region, self._user_pool_id)
        with urllib.request.urlopen(keys_url) as request:
            response = request.read()
        self._cognito_keys = json.loads(response.decode('utf-8'))['keys']

    def _verify_jwt_token(self, jwt: JwtToken):
        # jwt.
        pass
