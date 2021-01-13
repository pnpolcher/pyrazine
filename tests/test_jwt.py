import json
import unittest
from typing import Dict

from pyrazine.jwt import JwtToken, CognitoJwtToken

COGNITO_ACCESS_TOKEN_FILE = 'tests/cognito_access_token.json'
COGNITO_ID_TOKEN_FILE = 'tests/cognito_id_token.json'


def _load_access_token() -> Dict[str, object]:
    with open(COGNITO_ACCESS_TOKEN_FILE, "r") as jwt_file:
        access_token = json.load(jwt_file)

    return access_token["jwt"]["claims"]


def _load_id_token() -> Dict[str, object]:
    with open(COGNITO_ID_TOKEN_FILE, "r") as jwt_file:
        id_token = json.load(jwt_file)

    return id_token["jwt"]["claims"]


class TestJwtToken(unittest.TestCase):
    """
    Tests the JwtToken class.
    """

    def setUp(self) -> None:
        self._access_token = _load_access_token()
        self._id_token = _load_id_token()

    def _assert_access_token(self, token: JwtToken):
        self.assertEqual(token.aud, None)
        self.assertEqual(token.exp, self._access_token["exp"])
        self.assertEqual(token.iat, self._access_token["iat"])
        self.assertEqual(token.iss, self._access_token["iss"])
        self.assertEqual(token.jti, self._access_token["jti"])
        self.assertEqual(token.sub, self._access_token["sub"])

    def _assert_access_dict(self, d: Dict[str, object]):
        self.assertEqual(d["aud"], None)
        self.assertEqual(d["exp"], self._access_token["exp"])
        self.assertEqual(d["iat"], self._access_token["iat"])
        self.assertEqual(d["iss"], self._access_token["iss"])
        self.assertEqual(d["jti"], self._access_token["jti"])
        self.assertEqual(d["sub"], self._access_token["sub"])

    def _assert_id_token(self, token: JwtToken):
        self.assertEqual(token.aud, self._id_token["aud"])
        self.assertEqual(token.exp, self._id_token["exp"])
        self.assertEqual(token.iat, self._id_token["iat"])
        self.assertEqual(token.iss, self._id_token["iss"])
        self.assertEqual(token.jti, None)
        self.assertEqual(token.sub, self._id_token["sub"])

    def _assert_id_dict(self, d: Dict[str, object]):
        self.assertEqual(d["aud"], self._id_token["aud"])
        self.assertEqual(d["exp"], self._id_token["exp"])
        self.assertEqual(d["iat"], self._id_token["iat"])
        self.assertEqual(d["iss"], self._id_token["iss"])
        self.assertEqual(d["jti"], None)
        self.assertEqual(d["sub"], self._id_token["sub"])

    def test_jwt_properties_with_access_token_dict(self):
        token = JwtToken(token_object=self._access_token)
        self._assert_access_token(token)

    def test_jwt_dict_with_access_token_dict(self):
        token = JwtToken(token_object=self._access_token)
        d = token.as_dict()
        self._assert_access_dict(d)

    def test_jwt_properties_with_id_token_dict(self):
        token = JwtToken(token_object=self._id_token)
        self._assert_id_token(token)

    def test_jwt_dict_with_id_token_dict(self):
        token = JwtToken(token_object=self._id_token)
        d = token.as_dict()
        self._assert_id_dict(d)

    def test_jwt_properties_with_access_token_string(self):
        token_str = json.dumps(self._access_token)
        token = JwtToken(token_string=token_str)
        self._assert_access_token(token)

    def test_jwt_dict_with_access_token_string(self):
        token_str = json.dumps(self._access_token)
        token = JwtToken(token_string=token_str)
        d = token.as_dict()
        self._assert_access_dict(d)

    def test_jwt_properties_with_id_token_string(self):
        token_str = json.dumps(self._id_token)
        token = JwtToken(token_string=token_str)
        self._assert_id_token(token)

    def test_jwt_dict_with_id_token_string(self):
        token_str = json.dumps(self._id_token)
        token = JwtToken(token_string=token_str)
        d = token.as_dict()
        self._assert_id_dict(d)


class TestCognitoJwt(unittest.TestCase):

    def setUp(self) -> None:
        self._access_token = _load_access_token()
        self._id_token = _load_id_token()

    def _assert_access_token(self, token: CognitoJwtToken):
        self.assertEqual(token.auth_time, self._access_token["auth_time"])
        self.assertEqual(token.client_id, self._access_token["client_id"])
        self.assertEqual(token.cognito_username, None)
        self.assertEqual(token.email, None)
        self.assertEqual(token.event_id, self._access_token["event_id"])
        self.assertEqual(token.scope, self._access_token["scope"])
        self.assertEqual(token.token_use, self._access_token["token_use"])
        self.assertEqual(token.username, self._access_token["username"])

    def _assert_access_dict(self, d: Dict[str, object]):
        self.assertEqual(d["auth_time"], self._access_token["auth_time"])
        self.assertEqual(d["client_id"], self._access_token["client_id"])
        self.assertEqual(d["cognito_username"], None)
        self.assertEqual(d["email"], None)
        self.assertEqual(d["event_id"], self._access_token["event_id"])
        self.assertEqual(d["scope"], self._access_token["scope"])
        self.assertEqual(d["token_use"], self._access_token["token_use"])
        self.assertEqual(d["username"], self._access_token["username"])

    def _assert_id_token(self, token: CognitoJwtToken):
        self.assertEqual(token.auth_time, self._id_token["auth_time"])
        self.assertEqual(token.client_id, None)
        self.assertEqual(token.cognito_username, self._id_token["cognito:username"])
        self.assertEqual(token.email, self._id_token["email"])
        self.assertEqual(token.event_id, self._id_token["event_id"])
        self.assertEqual(token.scope, None)
        self.assertEqual(token.token_use, self._id_token["token_use"])
        self.assertEqual(token.username, None)

    def _assert_id_dict(self, d: Dict[str, object]):
        self.assertEqual(d["auth_time"], self._id_token["auth_time"])
        self.assertEqual(d["client_id"], None)
        self.assertEqual(d["cognito_username"], self._id_token["cognito:username"])
        self.assertEqual(d["email"], self._id_token["email"])
        self.assertEqual(d["event_id"], self._id_token["event_id"])
        self.assertEqual(d["scope"], None)
        self.assertEqual(d["token_use"], self._id_token["token_use"])
        self.assertEqual(d["username"], None)

    def test_jwt_properties_with_access_token_dict(self):
        token = CognitoJwtToken(token_object=self._access_token)
        self._assert_access_token(token)

    def test_jwt_dict_with_access_token_dict(self):
        token = CognitoJwtToken(token_object=self._access_token)
        d = token.as_dict()
        self._assert_access_dict(d)

    def test_jwt_properties_with_id_token_dict(self):
        token = CognitoJwtToken(token_object=self._id_token)
        self._assert_id_token(token)

    def test_jwt_dict_with_id_token_dict(self):
        token = CognitoJwtToken(token_object=self._id_token)
        d = token.as_dict()
        self._assert_id_dict(d)

    def test_jwt_properties_with_access_token_string(self):
        token_str = json.dumps(self._access_token)
        token = CognitoJwtToken(token_string=token_str)
        self._assert_access_token(token)

    def test_jwt_dict_with_access_token_string(self):
        token_str = json.dumps(self._access_token)
        token = CognitoJwtToken(token_string=token_str)
        d = token.as_dict()
        self._assert_access_dict(d)

    def test_jwt_properties_with_id_token_string(self):
        token_str = json.dumps(self._id_token)
        token = CognitoJwtToken(token_string=token_str)
        self._assert_id_token(token)

    def test_jwt_dict_with_id_token_string(self):
        token_str = json.dumps(self._id_token)
        token = CognitoJwtToken(token_string=token_str)
        d = token.as_dict()
        self._assert_id_dict(d)


class TestJwtTokenParser(unittest.TestCase):

    def setUp(self) -> None:
        pass

    @staticmethod
    def _build_proxy_object(jwt_object: Dict[str, object]) -> Dict[str, object]:
        return {
            'requestContext': {
                'authorizer': jwt_object
            }
        }


class TestJwtTokenJsonEncoder(unittest.TestCase):

    def setUp(self) -> None:
        pass
