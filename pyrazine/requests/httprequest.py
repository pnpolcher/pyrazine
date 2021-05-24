from typing import Any, Dict, Optional

from pyrazine.context import RequestContext


class HttpRequest(object):
    _payload: Any
    _cookies: Dict[str, str]
    _headers: Dict[str, str]
    _path_variables: Dict[str, Any]
    _context: RequestContext
    _query_string: Dict[Any, list]

    def __init__(self,
                 payload: Any,
                 cookies: Optional[Dict[str, str]] = None,
                 headers: Optional[Dict[str, str]] = None,
                 query_string: Optional[Dict[Any, list]] = None,
                 path_variables: Optional[Dict[str, Any]] = None,
                 context: Optional[RequestContext] = None):

        self._payload = payload
        self._cookies = cookies or []
        self._headers = headers or {}
        self._path_variables = path_variables or {}
        self._context = context or RequestContext()
        self._query_string = query_string or {}

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
             query_string: Optional[Dict[Any, list]] = None):

        merged_cookies = cookies or {}
        merged_cookies.update(self._cookies)

        merged_headers = headers or {}
        merged_headers.update(self._headers)

        merged_query_string = query_string or {}
        merged_query_string.update(self._query_string)

        pathvars = path_variables or {}
        pathvars.update(self._path_variables)

        return self.__class__(
            cookies=merged_cookies,
            headers=merged_headers,
            path_variables=pathvars,
            context=context,
            query_string=merged_query_string
        )
