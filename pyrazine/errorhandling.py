from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, Optional

from pyrazine.exceptions import (
    BadRequestError,
    HttpForbiddenError,
    MethodNotAllowedError,
)
from pyrazine.response import HttpResponse


class BaseErrorHandler(ABC):
    """
    An abstract class that models what a basic error handler should minimally
    implement to be used in Pyrazine.
    """

    @abstractmethod
    def get_error_body(self, message: str, data: Dict[str, Any]):
        raise NotImplementedError('Method not implemented in abstract class.')

    @abstractmethod
    def get_response(self, e: Exception, ctx: Dict[str, Any]) -> HttpResponse:
        """
        Creates an instance of the HttpResponse class with an error code that
        corresponds to the exception thrown.

        :param e: The exception based on which a message is produced.
        :param ctx: The context in which the error occurred. Can be used to
        enrich the error message.
        :return: An instance of the HttpResponse class with an appropriate
        error message for the exception thrown.
        """
        raise NotImplementedError('Method not implemented in abstract class.')


class DefaultErrorHandler(BaseErrorHandler):

    def get_error_body(self, message: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'message': message,
            'data': data,
        }

    def get_response(self, e: Exception, ctx: Dict[str, Any]) -> HttpResponse:
        if isinstance(e, BadRequestError):
            response = HttpResponse(
                400, self.get_error_body(
                    'Bad request', {
                        'message': str(e),
                    }
                )
            )
        elif isinstance(e, MethodNotAllowedError):
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
