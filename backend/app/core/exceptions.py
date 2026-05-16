class AppError(Exception):
    """Base application error mapped to HTTP responses."""

    status_code: int = 500
    detail: str = "Internal server error"

    def __init__(self, detail: str | None = None):
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class ConfigurationError(AppError):
    status_code = 500
    detail = "Server is not configured correctly"


class UnauthorizedError(AppError):
    status_code = 401
    detail = "Invalid or expired token"


class NotFoundError(AppError):
    status_code = 404
    detail = "Not found"


class BadRequestError(AppError):
    status_code = 400
    detail = "Bad request"


class DatabaseError(AppError):
    status_code = 503
    detail = "Database unavailable"
