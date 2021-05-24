from typing import Any, Dict, Optional


class RequestContext(object):

    _context_vars: Dict[str, Any]
    _profile: Any

    def __init__(self,
                 context_vars: Optional[Dict[str, Any]] = None,
                 profile: Optional[Any] = None):

        self._context_vars = context_vars or {}
        self._profile = profile or None

    @property
    def context_vars(self) -> Dict[str, Any]:
        return self._context_vars

    @property
    def profile(self) -> Any:
        return self._profile

    def copy(self,
             context_vars: Optional[Dict[str, Any]] = None,
             profile: Optional[Any] = None):

        merged_context_vars = context_vars or {}
        merged_context_vars.update(self._context_vars)

        return self.__class__(
            context_vars=merged_context_vars,
            profile=profile
        )
