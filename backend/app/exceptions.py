class AppError(Exception):
    """Application error with an HTTP status code."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class DocumentNotFoundError(AppError):
    def __init__(self, document_id: str) -> None:
        super().__init__(f"Document '{document_id}' was not found.", status_code=404)


class InvalidUploadError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=400)


class ProcessingError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=500)
