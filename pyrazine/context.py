from typing import Any, Dict, Optional


class RequestContext(object):

    _path_variables: Dict[str, Any]
    _profile: Any

    def __init__(self,
                 path_variables: Optional[Dict[str, Any]] = None,
                 profile: Optional[Any] = None):

        self._path_variables = path_variables or {}
        self._profile = profile

    @property
    def path_variables(self) -> Dict[str, Any]:
        return self._path_variables

    @property
    def profile(self) -> Any:
        return self._profile

    def copy(self,
             path_variables: Optional[Dict[str, Any]] = None,
             profile: Optional[Any] = None):

        pathvars = path_variables or {}
        pathvars.update(self.path_variables)

        return self.__class__(pathvars, profile)
