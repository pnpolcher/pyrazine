from pyrazine.jwt import JwtTokenParser


class HttpEvent(object):

    def __init__(self, event):

        self.version = event.get('version')
        self.route_key = event.get('routeKey')
        self.raw_path = event.get('rawPath')
        self.raw_query_string = event.get('rawQueryString')
        self.headers = event.get('headers')
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
            self.jwt = JwtTokenParser.parse_object(jwt) \
                if jwt is not None else None
        else:
            self.jwt = None

    def get_account_id(self) -> str:
        return str(self.request_context['accountId']) \
            if 'accountId' in self.request_context else None

    def get_api_id(self) -> str:
        return str(self.request_context['apiId']) \
            if 'apiId' in self.request_context else None

    def get_domain_name(self) -> str:
        return str(self.request_context['domainName']) \
            if 'domainName' in self.request_context else None

    def get_domain_prefix(self) -> str:
        return str(self.request_context['domainPrefix']) \
            if 'domainPrefix' in self.request_context else None

    def get_http_method(self) -> str:
        return str(self.http_context['method']) \
            if 'method' in self.http_context else None

    def get_http_path(self) -> str:
        return str(self.http_context['path']) \
            if 'path' in self.http_context else None

    def get_http_protocol(self) -> str:
        return str(self.http_context['protocol']) \
            if 'protocol' in self.http_context else None

    def get_http_source_ip(self) -> str:
        return str(self.http_context['sourceIp']) \
            if 'sourceIp' in self.http_context else None

    def get_http_user_agent(self) -> str:
        return str(self.http_context['userAgent']) \
            if 'userAgent' in self.http_context else None

    def get_path(self) -> str:
        result = self.path_parameters.get('proxy') or \
            self.http_context.get('path')
        return result if result is None else str(result)

    def get_request_epoch(self) -> str:
        return str(self.request_context['timeEpoch']) \
            if 'timeEpoch' in self.request_context else None

    def get_request_id(self):
        return str(self.request_context['requestId']) \
            if 'requestId' in self.request_context else None

    def get_request_time(self):
        return str(self.request_context['time']) \
            if 'time' in self.request_context else None

    def get_route_key(self):
        return str(self.request_context['routeKey']) \
            if 'routeKey' in self.request_context else None

    def get_stage(self):
        return str(self.request_context['stage']) \
            if 'stage' in self.request_context else None
