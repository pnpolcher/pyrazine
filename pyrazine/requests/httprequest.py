from typing import Any, Dict, Optional

from pyrazine.context import RequestContext
from pyrazine.jwt import JwtToken


class HttpRequest(object):
    _context: RequestContext
    _cookies: Dict[str, str]
    _headers: Dict[str, str]
    _jwt_token: JwtToken
    _path_variables: Dict[str, Any]
    _payload: Any
    _query_string: Dict[Any, list]

    def __init__(self,
                 payload: Any,
                 cookies: Optional[Dict[str, str]] = None,
                 headers: Optional[Dict[str, str]] = None,
                 query_string: Optional[Dict[Any, list]] = None,
                 path_variables: Optional[Dict[str, Any]] = None,
                 context: Optional[RequestContext] = None,
                 jwt_token: Optional[JwtToken] = None):

        self._payload = payload
        self._cookies = cookies or []
        self._headers = headers or {}
        self._path_variables = path_variables or {}
        self._context = context or RequestContext()
        self._query_string = query_string or {}
        self._jwt_token = jwt_token or None

    @property
    def context(self) -> RequestContext:
        return self._context

    @property
    def cookies(self) -> Dict[str, str]:
        return self._cookies

    @property
    def headers(self) -> Dict[str, str]:
        return self._headers

    @property
    def jwt_token(self) -> JwtToken:
        return self._jwt_token

    @property
    def path_variables(self) -> Dict[str, Any]:
        return self._path_variables

    @property
    def payload(self) -> Any:
        return self._payload

    @property
    def query_string(self) -> Dict[Any, list]:
        return self._query_string

    def copy(self,
             cookies: Optional[Dict[str, str]] = None,
             headers: Optional[Dict[str, str]] = None,
             path_variables: Optional[Dict[str, Any]] = None,
             context: Optional[RequestContext] = None,
             query_string: Optional[Dict[Any, list]] = None,
             jwt_token: Optional[JwtToken] = None,
             payload: Optional[Any] = None):

        merged_cookies = cookies or {}
        merged_cookies.update(self._cookies)

        merged_headers = headers or {}
        merged_headers.update(self._headers)

        merged_query_string = query_string or {}
        merged_query_string.update(self._query_string)

        pathvars = path_variables or {}
        pathvars.update(self._path_variables)

        return self.__class__(
            payload or self.payload,
            cookies=merged_cookies,
            headers=merged_headers,
            path_variables=pathvars,
            context=context,
            query_string=merged_query_string,
            jwt_token=jwt_token or self._jwt_token,
        )
