import json
from typing import Tuple
import unittest
from unittest.mock import Mock

from pyrazine.handlers import LambdaHandler
from pyrazine.response import HttpResponse


class TestLambdaHandler(unittest.TestCase):

    TEST_HTTP_EVENT = {
        "version": "2.0",
        "routeKey": "ANY /",
        "rawPath": "/",
        "rawQueryString": "",
        "cookies": [],
        "headers": {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
        },
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "r3pmxmplak",
            "domainName": "r3pmxmplak.execute-api.us-east-2.amazonaws.com",
            "domainPrefix": "r3pmxmplak",
            "http": {
                "method": "GET",
                "path": "/",
                "protocol": "HTTP/1.1",
                "sourceIp": "205.255.255.176",
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
            },
            "requestId": "JKJaXmPLvHcESHA=",
            "routeKey": "ANY /",
            "stage": "default",
            "time": "10/Mar/2020:05:16:23 +0000",
            "timeEpoch": 1583817383220
        },
        "isBase64Encoded": True
    }

    @staticmethod
    def _get_mock_recorder() -> Tuple[Mock, Mock]:
        mock_recorder = Mock()

        mock_subsegment_ctxmgr = Mock()
        mock_recorder.in_subsegment.return_value = mock_subsegment_ctxmgr

        mock_subsegment = Mock()
        mock_subsegment_ctxmgr.__enter__ = lambda *args: mock_subsegment
        mock_subsegment_ctxmgr.__exit__ = lambda *args: None

        return mock_recorder, mock_subsegment

    @staticmethod
    def _is_route_registered(method: str, path: str, handler: LambdaHandler):
        return method in handler._routes and path in handler._routes[method]

    @staticmethod
    def _get_route_fn(method: str, path: str, handler: LambdaHandler):
        return handler._routes[method][path]

    def setUp(self) -> None:
        pass

    def test_route_registration_no_trace(self):
        """
        Tests that a route has been registered, and that tracing is disabled for that route.
        :return:
        """

        handler = LambdaHandler(trace=False)

        @handler.route(path='/', methods=('GET',))
        def test_method_no_trace(token, body, context):
            return HttpResponse(200)

        # Make sure the route has been registered.
        self.assertTrue(self._is_route_registered('GET', '/', handler))

        # Make sure the function associated is the same we registered.
        self.assertEqual(
            self._get_route_fn('GET', '/', handler),
            test_method_no_trace)

    def test_tracing_in_registered_route(self):
        """
        Tests that a route that has been registered with tracing enabled is
        calling the methods required for AWS X-Ray tracing.
        :return:
        """

        mock_recorder, mock_subsegment = self._get_mock_recorder()
        handler = LambdaHandler(recorder=mock_recorder)

        @handler.route(path='/', methods=('GET',))
        def test_method(token, body, context):
            return HttpResponse(200)

        # Call the function associated with the route.
        handler.handle_request(self.TEST_HTTP_EVENT, {})

        # Check that the in_subsegment method was called to obtain a
        # subsegment object.
        mock_recorder.in_subsegment.assert_called_with(
            name=f'## {test_method.__name__}')

        # Check that the put_annotation method was called to store the
        # cold start status of the call.
        mock_subsegment.put_annotation.assert_called_with(
            key='ColdStart', value=True)

    def test_route_response(self):
        """
        Tests that the response returned from the route handler has not
        been tampered with.

        :return:
        """

        handler = LambdaHandler(trace=False)

        @handler.route(path='/', methods=('GET',))
        def test_method(token, body, context):
            return HttpResponse(200, {'test_key': 'test_value'})

        # Call the function associated with the route.
        response = handler.handle_request(self.TEST_HTTP_EVENT, {})

        self.assertEqual(response['statusCode'], 200)

        test_body = json.loads(response['body'])
        self.assertEqual(test_body['test_key'], 'test_value')

    def test_route_error_message(self):
        """

        :return:
        """

        handler = LambdaHandler(trace=False)

        @handler.route(path='/', methods=('GET',))
        def test_handler(token, body, context):
            return HttpResponse(500, message='Test error')

        # Call the function associated with the route.
        response = handler.handle_request(self.TEST_HTTP_EVENT, {})

        self.assertEqual(response['statusCode'], 500)

        test_body = json.loads(response['body'])
        self.assertEqual(test_body['error']['message'], 'Test error')
