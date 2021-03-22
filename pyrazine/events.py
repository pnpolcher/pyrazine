import logging
import re
from typing import Any, Dict
from urllib.parse import parse_qs

from pyrazine.jwt import JwtTokenParser


logger = logging.getLogger()


class HttpEvent(object):
    """
    Models the data found in the event passed to the Lambda function.
    """

    def __init__(self, event):

        self._version = event.get('version')
        self.route_key = event.get('routeKey')
        self.raw_path = event.get('rawPath')
        self.raw_query_string = event.get('rawQueryString')
        self.headers = event.get('headers')
        self.cookies = event.get('cookies')

        self.request_context = event.get('requestContext')
        if self.request_context is None:
            raise ValueError('Event does not contain request_context key.')

        self.http_context = self.request_context.get('http')
        if self.http_context is None:
            raise ValueError('No HTTP context information.')

        self.path_parameters = event.get('pathParameters') or {}
        self.body = event.get('body')
        self.is_base64_encoded = event.get('isBase64Encoded')

        self.authorizer = self.request_context.get('authorizer')
        if self.authorizer is not None and 'jwt' in self.authorizer:
            jwt = self.authorizer['jwt']['claims']
            if jwt is not None:
                self.jwt = JwtTokenParser.parse_object(jwt)
                self.jwt.raw_token = self._get_jwt_from_headers()
            else:
                logger.debug('No authorizer data found.')
                self.jwt = None
        else:
            self.jwt = None

    def _get_jwt_from_headers(self):
        if self.headers is not None and 'authorization' in self.headers:
            m = re.match('[Bb]earer\\s+(.*)', self.headers['authorization'])
            token = m[1].strip() if m is not None and len(m.groups()) == 1 else None
        else:
            logger.debug('No authorization header found.')
            token = None

        return token

    @property
    def query_string(self) -> Dict[Any, list]:
        return parse_qs(self.raw_query_string)

    @property
    def req_ctx_account_id(self) -> str:
        return str(self.request_context['accountId']) \
            if 'accountId' in self.request_context else None

    @property
    def req_ctx_api_id(self) -> str:
        return str(self.request_context['apiId']) \
            if 'apiId' in self.request_context else None

    @property
    def req_ctx_domain_name(self) -> str:
        return str(self.request_context['domainName']) \
            if 'domainName' in self.request_context else None

    @property
    def req_ctx_domain_prefix(self) -> str:
        return str(self.request_context['domainPrefix']) \
            if 'domainPrefix' in self.request_context else None

    @property
    def http_ctx_method(self) -> str:
        return str(self.http_context['method']) \
            if 'method' in self.http_context else None

    @property
    def http_ctx_path(self) -> str:
        return str(self.http_context['path']) \
            if 'path' in self.http_context else None

    @property
    def http_ctx_protocol(self) -> str:
        return str(self.http_context['protocol']) \
            if 'protocol' in self.http_context else None

    @property
    def http_ctx_source_ip(self) -> str:
        return str(self.http_context['sourceIp']) \
            if 'sourceIp' in self.http_context else None

    @property
    def http_ctx_user_agent(self) -> str:
        return str(self.http_context['userAgent']) \
            if 'userAgent' in self.http_context else None

    @property
    def path(self) -> str:
        result = self.path_parameters.get('proxy') or \
            self.http_context.get('path')
        return result if result is None else str(result)

    @property
    def req_ctx_time_epoch(self) -> str:
        return str(self.request_context['timeEpoch']) \
            if 'timeEpoch' in self.request_context else None

    @property
    def req_ctx_request_id(self):
        return str(self.request_context['requestId']) \
            if 'requestId' in self.request_context else None

    @property
    def req_ctx_time(self):
        return str(self.request_context['time']) \
            if 'time' in self.request_context else None

    @property
    def req_ctx_route_key(self):
        return str(self.request_context['routeKey']) \
            if 'routeKey' in self.request_context else None

    @property
    def req_ctx_stage(self):
        return str(self.request_context['stage']) \
            if 'stage' in self.request_context else None

    @property
    def version(self) -> str:
        return self._version
