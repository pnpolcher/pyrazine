import json
from typing import Any, Sequence
import unittest

import aws_xray_sdk.core as xray_core
from aws_xray_sdk.core.models.subsegment import Subsegment
from moto import mock_xray_client, XRaySegment
from moto.xray.mock_client import MockEmitter

from pyrazine.auth.base import BaseAuthorizer
from pyrazine.exceptions import BadRequestError, HttpForbiddenError
from pyrazine.handlers import ApiGatewayEventHandler
from pyrazine.jwt import JwtToken
from pyrazine.response import HttpResponse
from pyrazine.typing import LambdaContext


class MockAuthorizer(BaseAuthorizer):
    def authorizer(self,
                   roles: Sequence[str],
                   token: JwtToken,
                   fetch_full_profile: bool = False) -> Any:

        if 'right_role' not in roles:
            raise HttpForbiddenError()
        else:
            return {}


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
    def _get_lambda_context(function_name: str) -> LambdaContext:
        return LambdaContext(function_name, '1', 'arn', 128,
                             'req_id', 'log_group_name', 'log_stream_name',
                             None, None)

    @mock_xray_client
    def test_tracing_in_registered_route(self):
        """
        Tests that a route that has been registered with tracing enabled is
        calling the methods required for AWS X-Ray tracing.
        :return:
        """

        self.assertIsInstance(xray_core.xray_recorder._emitter, MockEmitter)

        handler = ApiGatewayEventHandler()

        @handler.route(path='/', methods=('GET',))
        def test_method(token, body, context):
            return HttpResponse(200)

        # Call the function associated with the route.
        with XRaySegment():
            handler.handle_request(self.TEST_HTTP_EVENT, self._get_lambda_context('TestFunction'))

            segment = xray_core.xray_recorder.current_segment()
            self.assertEqual(len(segment.subsegments), 1)

            subsegment: Subsegment = segment.subsegments[0]
            self.assertEqual(subsegment.name, '## test_method')
            self.assertTrue(subsegment.annotations['ColdStart'])

    def test_route_response(self):
        """
        Tests that the response returned from the route handler has not
        been tampered with.

        :return:
        """

        handler = ApiGatewayEventHandler(trace=False)

        @handler.route(path='/', methods=('GET',))
        def test_method(token, body, context):
            return HttpResponse(200, {'test_key': 'test_value'})

        # Call the function associated with the route.
        response = handler.handle_request(
            self.TEST_HTTP_EVENT, self._get_lambda_context('TestFunction'))

        self.assertEqual(response['statusCode'], 200)

        test_body = json.loads(response['body'])
        self.assertEqual(test_body['test_key'], 'test_value')

    def test_route_error_message(self):
        """

        :return:
        """

        handler = ApiGatewayEventHandler(trace=False)

        @handler.route(path='/', methods=('GET',))
        def test_handler(token, body, context):
            return HttpResponse(500, message='Test error')

        # Call the function associated with the route.
        response = handler.handle_request(
            self.TEST_HTTP_EVENT, self._get_lambda_context('TestFunction'))

        self.assertEqual(response['statusCode'], 500)

        test_body = json.loads(response['body'])
        self.assertEqual(test_body['error']['message'], 'Test error')

    def test_route_exception_to_response(self):
        handler = ApiGatewayEventHandler(trace=False)

        @handler.route(path='/', methods=('GET',))
        def test_handler(token, body, context):
            raise BadRequestError('Invalid parameter.')

        response = handler.handle_request(
            self.TEST_HTTP_EVENT, self._get_lambda_context('TestFunction'))

        self.assertEqual(response['statusCode'], 400)
        response_body = json.loads(response['body'])
        self.assertEqual(response_body['error']['message'], 'Invalid parameter.')

    def test_route_authorization_when_right_role(self):

        handler = ApiGatewayEventHandler(trace=False, authorizer=MockAuthorizer())

        @handler.route(path='/', methods=('GET', ), authorization=True, roles=['right_role'])
        def test_handler(token, body, context):
            return HttpResponse()

        response = handler.handle_request(
            self.TEST_HTTP_EVENT, self._get_lambda_context('TestFunction'))

        self.assertEqual(response['statusCode'], 200)

    def test_route_authorization_when_wrong_role(self):

        handler = ApiGatewayEventHandler(trace=False, authorizer=MockAuthorizer())

        @handler.route(path='/', methods=('GET', ), authorization=True, roles=['wrong_role'])
        def test_handler(token, body, context):
            return HttpResponse()

        response = handler.handle_request(
            self.TEST_HTTP_EVENT, self._get_lambda_context('TestFunction'))

        self.assertEqual(response['statusCode'], 403)
