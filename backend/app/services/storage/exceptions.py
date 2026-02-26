"""Google Drive storage service exceptions."""
from typing import Optional


class GoogleDriveStorageError(Exception):
    """Base exception for Google Drive storage errors."""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[dict] = None):
        self.message = message
        self.code = code or "STORAGE_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(GoogleDriveStorageError):
    """Raised when Google Drive authentication fails."""
    
    def __init__(self, message: str = "Google Drive authentication failed", details: Optional[dict] = None):
        super().__init__(message, code="AUTH_ERROR", details=details)


class PermissionError(GoogleDriveStorageError):
    """Raised when there's insufficient permission to access a resource."""
    
    def __init__(self, message: str = "Insufficient permissions", details: Optional[dict] = None):
        super().__init__(message, code="PERMISSION_ERROR", details=details)


class NotFoundError(GoogleDriveStorageError):
    """Raised when a file or folder is not found."""
    
    def __init__(self, message: str = "Resource not found", details: Optional[dict] = None):
        super().__init__(message, code="NOT_FOUND", details=details)


class QuotaExceededError(GoogleDriveStorageError):
    """Raised when Google Drive storage quota is exceeded."""
    
    def __init__(self, message: str = "Storage quota exceeded", details: Optional[dict] = None):
        super().__init__(message, code="QUOTA_EXCEEDED", details=details)


class UploadError(GoogleDriveStorageError):
    """Raised when file upload fails."""
    
    def __init__(self, message: str = "File upload failed", details: Optional[dict] = None):
        super().__init__(message, code="UPLOAD_ERROR", details=details)


class DownloadError(GoogleDriveStorageError):
    """Raised when file download fails."""
    
    def __init__(self, message: str = "File download failed", details: Optional[dict] = None):
        super().__init__(message, code="DOWNLOAD_ERROR", details=details)


class RateLimitError(GoogleDriveStorageError):
    """Raised when API rate limit is exceeded."""
    
    def __init__(self, message: str = "API rate limit exceeded", details: Optional[dict] = None):
        super().__init__(message, code="RATE_LIMIT", details=details)
