from abc import ABC
from typing import Any, Dict, List, Optional


class BaseRequest(ABC):
    _cookies: List[str]
    _headers: Dict[str, str]
    _path_variables: Dict[str, Any]
    _profile: Any
    _query_string: Dict[Any, list]

    @property
    def cookies(self) -> List[str]:
        return self._cookies

    @property
    def headers(self) -> Dict[str, str]:
        return self._headers

    @property
    def path_variables(self) -> Dict[str, Any]:
        return self._path_variables

    @property
    def profile(self) -> Any:
        return self._profile

    @property
    def query_string(self) -> Dict[Any, list]:
        return self._query_string

    def copy(self,
             cookies: Optional[Dict[str, str]] = None,
             headers: Optional[Dict[str, str]] = None,
             path_variables: Optional[Dict[str, Any]] = None,
             profile: Optional[Any] = None,
             query_string: Optional[Dict[Any, list]] = None):
        merged_cookies = cookies or []
        #        merged_cookies.update(self.cookies)
        merged_cookies = merged_cookies + self.cookies

        merged_headers = headers or {}
        merged_headers.update(self.headers)

        merged_query_string = query_string or {}
        merged_query_string.update(self.query_string)

        pathvars = path_variables or {}
        pathvars.update(self.path_variables)

        return self.__class__(
            cookies=merged_cookies,
            headers=merged_headers,
            path_variables=pathvars,
            profile=profile,
            query_string=merged_query_string
        )
