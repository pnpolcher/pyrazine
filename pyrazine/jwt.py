import json
from typing import Dict, Union


class JwtToken(object):

    def __init__(self, token_object: Dict[str, object] = None, token_string: str = None):
        """
        Takes either a token object (a dictionary of objects indexed by strings), or a token
        string (a JSON-serialized token), and provides read-only access to the information contained
        in either one through a series of properties.

        If both a token object and a token string are provided, the object takes precedence over
        the string.

        :param token_object: A dictionary of objects indexed by strings with the contents of a JWT
        token.
        :param token_string: A string containing a JWT token, serialized as JSON.
        """
        if token_object is not None and isinstance(token_object, dict):
            self._token_contents = token_object
        elif token_string is not None and isinstance(token_string, str):
            self._token_contents = json.loads(token_string)
        else:
            raise ValueError('Invalid token contents provided.')

    @property
    def aud(self) -> str:
        """
        Token audience - The recipient(s) for which the token is intended.

        :return: The audience of the token, or None if the field is not present.
        """
        return str(self._token_contents['aud']) \
            if 'aud' in self._token_contents else None

    @property
    def exp(self) -> int:
        """
        Expiry - The time after which the token expires.

        :return: The date of expiration of the token, or None if the field is not present.
        """
        return int(self._token_contents['exp']) \
            if 'exp' in self._token_contents else None

    @property
    def iat(self) -> int:
        """
        Issued at - The time at which the token was issued.

        :return:
        """
        return int(self._token_contents['iat']) \
            if 'iat' in self._token_contents else None

    @property
    def iss(self) -> str:
        """
        Issuer -

        :return:
        """
        return str(self._token_contents['iss']) \
            if 'iss' in self._token_contents else None

    @property
    def jti(self) -> str:
        """
        JWT ID

        :return:
        """
        return str(self._token_contents['jti']) \
            if 'jti' in self._token_contents else None

    @property
    def sub(self) -> str:
        """
        Subject -

        :return:
        """
        return str(self._token_contents['sub']) \
            if 'sub' in self._token_contents else None

    def as_dict(self) -> Dict[str, object]:
        return {
            'aud': self.aud,
            'exp': self.exp,
            'iat': self.iat,
            'iss': self.iss,
            'jti': self.jti,
            'sub': self.sub
        }


class CognitoJwtToken(JwtToken):

    def __init__(self, token_object: Dict[str, object] = None, token_string: str = None):
        super().__init__(token_object, token_string)

    @property
    def auth_time(self) -> int:
        """
        The time when the authentication occurred.

        :return: Time of authentication as the number of seconds elapsed since 1970-01-01T0:0:0Z, if
        the field is present in the token. Otherwise, None.
        """
        return int(self._token_contents['auth_time']) \
            if 'auth_time' in self._token_contents else None

    @property
    def client_id(self) -> str:
        """
        Returns the client ID for which this token is intended.

        :return: The ID of the client for which this token is intended, if the field is present.
        Otherwise, None.
        """
        return str(self._token_contents['client_id']) \
            if 'client_id' in self._token_contents else None

    @property
    def cognito_username(self) -> str:
        """
        Returns the Cognito username associated to the user, to which this token has been issued.

        :return: The Cognito username, if the field is present in the token. Otherwise, None.
        """
        return str(self._token_contents['cognito:username']) \
            if 'cognito:username' in self._token_contents else None

    @property
    def email(self) -> str:
        """
        Returns the e-mail associated to the user, to which this token has been issued.

        :return: The e-mail, as stored in Amazon Cognito, if the field is present. Otherwise, None.
        """
        return str(self._token_contents['email']) \
            if 'email' in self._token_contents else None

    @property
    def email_verified(self) -> bool:
        """
        Returns True if the user, to which this token has been issued, has verified their e-mail
        in Amazon Cognito.

        :return: True, if the field is present, and the e-mail has been marked as verified in Amazon
        Cognito. In any other case, it returns False.
        """
        return bool(self._token_contents['email_verified']) \
            if 'email_verified' in self._token_contents else False

    @property
    def event_id(self) -> str:
        """
        Returns the ID of the event associated with this token.

        :return: The ID of the event associated with this token, if the field is present.
        Otherwise, None.
        """
        return str(self._token_contents['event_id']) \
            if 'event_id' in self._token_contents else None

    @property
    def family_name(self) -> str:
        """
        Returns the family name associated with the user to which this token has been issued.

        :return: If the field is present, the family name of the user, as stored in Amazon Cognito.
        Otherwise, None.
        """
        return str(self._token_contents['family_name']) \
            if 'family_name' in self._token_contents else None

    @property
    def given_name(self) -> str:
        """
        Returns the given name associated with the user to which this token has been issued.

        :return: If the field is present, the given name of the user, as stored in Amazon Cognito.
        Otherwise, None.
        """
        return str(self._token_contents['given_name']) \
            if 'given_name' in self._token_contents else None

    @property
    def scope(self) -> str:
        """
        Returns the scope.

        :return: The scope, if the field is present. Otherwise, None.
        """
        return str(self._token_contents['scope']) if 'scope' in self._token_contents else None

    @property
    def token_use(self) -> str:
        """
        Returns the use for which the token is intended.

        :return: The use for which the token is intended, if the field is present. Otherwise, None.
        """
        return str(self._token_contents['token_use']) \
            if 'token_use' in self._token_contents else None

    @property
    def username(self) -> str:
        """
        Returns the username to which this token has been issued.

        :return: The username to which this token has been issued, if the field is present.
        Otherwise, None.
        """
        return str(self._token_contents['username']) \
            if 'username' in self._token_contents else None

    def as_dict(self) -> Dict[str, object]:
        """
        Returns the token information as a dictionary of objects indexed by strings.

        :return: A dictionary of objects indexed by strings containing all fields in the token, and
        their respective values.
        """
        d = super().as_dict()

        d['auth_time'] = self.auth_time
        d['client_id'] = self.client_id
        d['cognito_username'] = self.cognito_username
        d['email'] = self.email
        d['email_verified'] = self.email_verified
        d['event_id'] = self.event_id
        d['family_name'] = self.family_name
        d['given_name'] = self.given_name
        d['scope'] = self.scope
        d['token_use'] = self.token_use
        d['username'] = self.username

        return d


class JwtTokenParser(object):
    """
    Provides static methods to parse JWT tokens that have either been serialized as JSON strings, or
    whose fields are stored in a dictionary.
    """

    @staticmethod
    def parse_string(token_string: str) -> JwtToken:
        """
        Parses a JWT token that is serialized as a JSON string.

        :param token_string: The JSON string to parse.
        :return: An object of type JwtToken with the contents of the token.
        """
        token_object = json.loads(token_string)
        return JwtTokenParser.parse_object(token_object)

    @staticmethod
    def parse_object(token_object: Dict[str, object]) -> Union[JwtToken, CognitoJwtToken]:
        """
        Factory method that creates a token class based on the contents of the token dictionary
        provided.

        :param token_object: A dictionary of objects indexed by strings that contains the fields
        of the JWT token for which to build a container object.
        :return: An object of either JwtToken or CognitoJwtToken type, depending on the contents
        of the dictionary.
        """
        if 'iss' not in token_object:
            raise ValueError('Invalid JWT token. No issuer.')

        iss = str(token_object['iss'])
        if iss.startswith('https://cognito-idp'):
            jwt_token = CognitoJwtToken(token_object=token_object)
        else:
            jwt_token = JwtToken(token_object=token_object)

        return jwt_token


class JwtTokenJsonEncoder(json.JSONEncoder):
    """
    Class that implements JSON serialization for objects of type JwtToken.
    """
    def default(self, o):
        if isinstance(o, JwtToken):
            return o.as_dict()
        else:
            return super().default(o)
