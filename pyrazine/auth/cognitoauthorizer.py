import functools
import json
import os
import time
from typing import Dict, List, Optional, Tuple

import urllib.request

from jose import jwk, jwt
from jose.utils import base64url_decode
from pyrazine.auth.base import (
    BaseAuthorizer,
    BaseAuthStorage,
    BaseUserProfile,
)
from pyrazine.exceptions import (
    InvalidTokenError,
    JwkNotFoundError,
    JwtVerificationFailedError,
    NotAuthorizedError,
)
from pyrazine.handlers import HandlerCallable
from pyrazine.jwt import JwtToken
from pyrazine.response import HttpResponse


class CognitoAuthorizer(BaseAuthorizer):
    """
    Implements a simple authorizer based on Amazon Cognito.
    """

    def __init__(self,
                 user_pool_id: str,
                 client_id: str,
                 region: str,
                 auth_storage: BaseAuthStorage):

        self._client_id = client_id
        self._user_pool_id = user_pool_id if user_pool_id is not None else \
            os.environ.get('COGNITO_USER_POOL')
        self._region = region if region is not None else os.environ.get('COGNITO_REGION')
        self._auth_storage = auth_storage

        self._initialize()

    def _initialize(self):
        keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json' \
            . format(self._region, self._user_pool_id)
        with urllib.request.urlopen(keys_url) as request:
            response = request.read()
        self._cognito_keys = json.loads(response.decode('utf-8'))['keys']

    def _verify_jwt_token(self, token: str):
        # Based on the code in:
        # https://github.com/awslabs/aws-support-tools/blob/master/Cognito/decode-verify-jwt/decode-verify-jwt.py

        if token is None:
            raise InvalidTokenError('')

        headers = jwt.get_unverified_headers(token)
        kid = headers['kid']

        key = next((k for k in self._cognito_keys if k['kid'] == kid), None)
        if key is None:
            raise JwkNotFoundError('')

        public_key = jwk.construct(key)

        # Get the last two sections of the token.
        message, encoded_signature = str(token).rsplit('.', 1)

        # Decode the signature.
        decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))

        if not public_key.verify(message.encode('utf8'), decoded_signature):
            raise JwtVerificationFailedError(
                JwtVerificationFailedError.INVALID_SIGNATURE,
                'Invalid token signature'
            )

        claims = jwt.get_unverified_claims(token)
        if time.time() > claims['exp']:
            # Token expired
            raise JwtVerificationFailedError(
                JwtVerificationFailedError.TOKEN_EXPIRED,
                'Token expired'
            )

        if claims['aud'] != self._client_id:
            # Token was not issued for this audience.
            raise JwtVerificationFailedError(
                JwtVerificationFailedError.INVALID_AUDIENCE,
                'Invalid audience'
            )

        return claims

    def _verify_roles(self,
                      user_id: str,
                      roles: List[str],
                      fetch_full_profile: bool = False) -> BaseUserProfile:

        # Fetch roles from database.
        if fetch_full_profile:
            profile = self._auth_storage.get_user_profile(user_id)
            user_roles = profile.roles
        else:
            profile = None
            user_roles = self._auth_storage.get_user_roles(user_id)

        # Check that all needed roles are present in the set.
        for role in roles:
            if role not in user_roles:
                raise NotAuthorizedError('Not authorized')

        return profile

    def auth(self,
             handler: HandlerCallable,
             roles: Optional[List[str], Tuple[str]],
             fetch_full_profile: bool = False) -> HandlerCallable:

        # TODO: Fetch user ID.
        user_id = ''

        @functools.wraps(handler)
        def wrapper(token: JwtToken, body: Dict[str, object]) -> HttpResponse:

            # TODO: Add raw token to JwtToken to be consumed here.
            self._verify_jwt_token(token.raw_token)
            profile = self._verify_roles(user_id, roles, fetch_full_profile)

            # TODO: Pass the profile to the handler in a context object.
            response = handler(token, body)
            return response

        return wrapper
