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


class NotAuthorizedError(Exception):
    pass
