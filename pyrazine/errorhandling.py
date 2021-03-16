from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, Optional

from pyrazine.exceptions import (
    HttpForbiddenError,
    MethodNotAllowedError,
)
from pyrazine.response import HttpResponse


class BaseErrorHandler(ABC):
    @abstractmethod
    def get_error_body(self, message: str, data: Dict[str, Any]):
        raise NotImplementedError('Method not implemented in abstract class.')

    @abstractmethod
    def get_response(self, e: Exception, ctx: Dict[str, Any]) -> HttpResponse:
        raise NotImplementedError('Method not implemented in abstract class.')


class DefaultErrorHandler(BaseErrorHandler):

    def get_error_body(self, message: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'message': message,
            'data': data,
        }

    def get_response(self, e: Exception, ctx: Dict[str, Any]) -> HttpResponse:
        if isinstance(e, MethodNotAllowedError):
            response = HttpResponse(
                405, self.get_error_body(
                    'Method not allowed', {
                        'method': e.method
                    }
                )
            )
        elif isinstance(e, HttpForbiddenError):
            response = HttpResponse(
                400, self.get_error_body(
                    'Not authorized', {}
                )
            )
        else:
            response = HttpResponse(
                500, self.get_error_body(
                    'Unknown error', {}
                )
            )

        return response
