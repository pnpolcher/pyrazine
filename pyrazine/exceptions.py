class BadRequestError(Exception):
    pass


class HttpNotFoundError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


class JwkNotFoundError(Exception):
    pass


class JwtVerificationFailedError(Exception):

    INVALID_SIGNATURE = 1
    TOKEN_EXPIRED = 2
    INVALID_AUDIENCE = 3

    def __init__(self, error_code: int, message: str):
        super().__init__(message)
        self._error_code = error_code

    @property
    def error_code(self) -> int:
        return self._error_code


class MethodNotAllowedError(Exception):

    def __init__(self, method: str, message: str):
        super().__init__(message)
        self._method = method

    @property
    def method(self) -> str:
        return self._method


class HttpForbiddenError(Exception):
    pass


class UserNotFoundError(Exception):
    _user_id: str

    def __init__(self, user_id: str, message: str):
        super().__init__(message)
        self._user_id = user_id

    @property
    def user_id(self) -> str:
        return self._user_id
