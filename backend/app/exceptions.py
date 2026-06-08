class AppException(Exception):
    status_code = 400

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code


class NotFoundException(AppException):
    status_code = 404


class UnauthorizedException(AppException):
    status_code = 401


class ForbiddenException(AppException):
    status_code = 403


class ConflictException(AppException):
    status_code = 409


class ValidationException(AppException):
    status_code = 422
