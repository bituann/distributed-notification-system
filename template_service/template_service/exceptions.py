class BaseException(Exception):
    """Base exception for the template service."""

    def __init__(self, message: str, detail: str = "", status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.detail = detail
        self.status_code = status_code


class NotFound(BaseException):
    def __init__(self, message: str = "Resource not found", detail: str = ""):
        super().__init__(message, detail, status_code=404)
