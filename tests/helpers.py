import base64
import json
import time
from typing import Any, Dict

from jose import jwt

from pyrazine.events import HttpEvent

JWT_SECRET = 'pyrazine'
TEST_BINARY_PAYLOAD = "Test binary payload".encode('utf-8')
TEST_EVENT_FILE = 'data/http_event.json'
TEST_JPEG_PAYLOAD_FILE = 'data/payload.jpg'
TEST_JSON_PAYLOAD = {'test': 'payload'}
TEST_PNG_PAYLOAD_FILE = 'data/payload.png'


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


def _get_binary_payload(b: bytes) -> str:
    return base64.b64encode(b).decode('utf-8')


def _get_event_epoch() -> int:
    return int(time.time() / 1000.0)


def _read_json_event(filename: str) -> Dict[str, Any]:
    with open(filename, 'r') as f:
        event = json.load(f)

    event['requestContext']['timeEpoch'] = _get_event_epoch()
    return event


def get_binary_payload_event() -> HttpEvent:
    ev = _read_json_event(TEST_EVENT_FILE)
    ev['body'] = _get_binary_payload(TEST_BINARY_PAYLOAD)
    ev['isBase64Encoded'] = True
    ev['headers']['content-type'] = 'application/octet-stream'
    return HttpEvent(ev)


def get_jpeg_payload_event() -> HttpEvent:
    ev = _read_json_event(TEST_EVENT_FILE)

    with open(TEST_JPEG_PAYLOAD_FILE, 'rb') as jpeg_file:
        ev['body'] = _get_binary_payload(jpeg_file.read())
    ev['isBase64Encoded'] = True
    ev['headers']['content-type'] = 'image/jpeg'
    return HttpEvent(ev)


def get_json_payload_event() -> HttpEvent:
    ev = _read_json_event(TEST_EVENT_FILE)
    ev['body'] = json.dumps(TEST_JSON_PAYLOAD)
    ev['isBase64Encoded'] = False
    ev['headers']['content-type'] = 'application/json'
    return HttpEvent(ev)


def get_png_payload_event() -> HttpEvent:
    ev = _read_json_event(TEST_EVENT_FILE)
    with open(TEST_PNG_PAYLOAD_FILE, 'rb') as png_file:
        ev['body'] = _get_binary_payload(png_file.read())
    ev['isBase64Encoded'] = True
    return HttpEvent(ev)
