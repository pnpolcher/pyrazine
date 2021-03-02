import time
from typing import Dict

from jose import jwt


JWT_SECRET = 'pyrazine'


def get_access_token() -> (Dict[str, object], str):

    claims = {
        'sub': 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
        'aud': '',
        'kid': '',
        'iss': 'https://cognito-idp.us-east-1.amazonaws.com/us-east-1_example',
        'exp': int(time.time()) + 86400,
    }

    token = jwt.encode(claims, JWT_SECRET, algorithm=jwt.ALGORITHMS.HS256)
    return claims, token
