import json
import time
import sys

from jose import jwt


JWT_SECRET = 'pyrazine'
claims = {
    'sub': 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
    'aud': '',
    'iss': 'https://cognito-idp.us-east-1.amazonaws.com/us-east-1_example',
    'exp': int(time.time()) + 86400,
}

token = jwt.encode(claims, JWT_SECRET, algorithm='HS256')

with open(f'./tests/integration/{sys.argv[1]}') as f:
    o = json.load(f)
    o['requestContext']['authorizer']['jwt']['claims'] = claims
    o['headers']['authorization'] = f"Bearer {token}"
    print(json.dumps(o))
