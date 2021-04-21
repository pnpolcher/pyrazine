import json
import logging
import os
import time
from typing import Any, Dict, List, Optional, Sequence

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
    HttpForbiddenError,
)
from pyrazine.jwt import JwtToken


logger = logging.getLogger()


class CognitoAuthorizer(BaseAuthorizer):
    """
    Implements a simple authorizer based on Amazon Cognito.
    """

    def __init__(self,
                 user_pool_id: str,
                 client_ids: Sequence[str],
                 region: str,
                 auth_storage: BaseAuthStorage,
                 verify_token: bool = True):

        self._client_ids = client_ids
        self._user_pool_id = user_pool_id if user_pool_id is not None else \
            os.environ.get('COGNITO_USER_POOL')
        self._region = region if region is not None else os.environ.get('COGNITO_REGION')
        self._auth_storage = auth_storage
        self._verify_token = verify_token

        if verify_token:
            self._initialize()

    def _initialize(self):
        keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json' \
            . format(self._region, self._user_pool_id)
        with urllib.request.urlopen(keys_url) as request:
            response = request.read()
        self._cognito_keys = json.loads(response.decode('utf-8'))['keys']

    def _verify_jwt_token(self, token: str) -> dict:
        # Based on the code in:
        # https://github.com/awslabs/aws-support-tools/blob/master/Cognito/decode-verify-jwt/decode-verify-jwt.py

        if not self._verify_token:
            return jwt.get_unverified_claims(token)

        if token is None:
            raise InvalidTokenError('No token was passed to verification function.')

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

        if 'aud' in claims and claims['aud'] not in self._client_ids:
            # Token was not issued for this audience.
            raise JwtVerificationFailedError(
                JwtVerificationFailedError.INVALID_AUDIENCE,
                'Invalid audience'
            )
        elif 'client_id' in claims and claims['client_id'] not in self._client_ids:
            # The expected client ID does not match that of the token.
            raise JwtVerificationFailedError(
                JwtVerificationFailedError.INVALID_AUDIENCE,
                'Invalid client ID'
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
            user_roles = self._auth_storage.get_user_roles(user_id)
            profile = {
                'roles': user_roles
            }

        # Check that all needed roles are present in the set.
        logger.debug(f'User roles: {user_roles}, required roles: {roles}')

        #
        if len(user_roles.intersection(roles)) == 0:
            raise HttpForbiddenError('Not authorized')

        return profile

    def authorizer(self,
                   roles: Sequence[str],
                   token: JwtToken,
                   auth_context: Optional[Dict[str, Any]] = None) -> Any:

        logger.debug(f'Cognito authorizer called.')

        auth_context = auth_context or {}
        fetch_full_profile = auth_context.get('fetch_full_profile', False)

        if roles is None:
            roles = []
        elif not isinstance(roles, list) and not isinstance(roles, tuple):
            raise TypeError('Allowed roles should be a list or tuple of strings.')

        # Verify the token.
        logger.debug('Verifying token.')
        self._verify_jwt_token(token.raw_token)

        # Verify whether the user has the necessary roles.
        # We use the sub claim as the user ID.
        logger.debug('Verifying roles.')
        profile = self._verify_roles(token.sub, roles, fetch_full_profile)

        logger.debug('Authorization checks passed.')
        return profile
