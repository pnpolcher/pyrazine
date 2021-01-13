import decimal
import json
from typing import Dict


class HttpResponseSerializer(json.JSONEncoder):
    """
    Class that implements serialization for types other than those supported
    by JSONEncoder, and that may come up in JSON in Lambda functions.
    """
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        else:
            return super().default(o)


class HttpResponse(object):
    """
    Encapsulates the necessary information to build a Lambda response object
    with HTTP status code and an optional body and/or error message.
    """

    def __init__(self,
                 status_code: int = 200,
                 body: object = None,
                 message: str = None,
                 enable_cors: bool = True):
        """

        :param status_code: The HTTP status code to return.

        :param body: The contents of the body in the HTTP response to send back
        to the client.

        :param message: If the HTTP status code is an error code (4xx or 5xx),
        then the message is populate the message field of the error object
        returned.

        :param enable_cors: Adds CORS headers to the response. Enabled by default.
        """

        self.status_code = status_code
        self.body = body
        self.message = message
        self._enable_cors = enable_cors

    @staticmethod
    def add_cors_headers(response):

        if 'headers' not in response:
            response['headers'] = {}

        response['headers']['access-control-allow-headers'] = \
            'content-type,x-amz-date,authorization,x-api-key,x-amz-security-token'
        response['headers']['access-control-allow-origin'] = '*'
        response['headers']['access-control-allow-methods'] = \
            'GET,POST,PUT,DELETE,OPTIONS'

    def get_response_object(self) -> Dict[str, object]:

        response = {
            'statusCode': self.status_code,
            'headers': {}
        }

        if 200 <= self.status_code < 400 and self.body is not None:
            response['body'] = json.dumps(
                self.body,
                cls=HttpResponseSerializer)
            response['headers']['content-type'] = 'application/json'
        else:
            response['body'] = json.dumps({
                'error': {
                    'message': self.message or 'Unknown error'
                }
            })

        if self._enable_cors:
            self.add_cors_headers(response)

        return response

    @classmethod
    def build_error_response(cls, status_code: int, message: str = None):
        return cls(status_code, message=message)

    @classmethod
    def build_success_response(cls, status_code: int = 200, body=None):
        return cls(status_code, body)
