"""Google Drive storage service implementation."""
import io
import logging
from typing import Optional, List, Dict, Any, BinaryIO
from datetime import datetime
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError

from app.core.config import settings
from app.services.storage.exceptions import (
    GoogleDriveStorageError,
    AuthenticationError,
    PermissionError,
    NotFoundError,
    QuotaExceededError,
    UploadError,
    DownloadError,
    RateLimitError,
)

logger = logging.getLogger(__name__)

# Google Drive API scopes
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
]


class GoogleDriveStorage:
    """Google Drive storage service for file operations."""
    
    def __init__(
        self,
        credentials: Optional[Credentials] = None,
        service=None,
    ):
        """Initialize Google Drive storage.
        
        Args:
            credentials: Google OAuth2 credentials
            service: Pre-built Drive service (for testing)
        """
        self._credentials = credentials
        self._service = service
    
    @property
    def service(self):
        """Lazy-load Google Drive service."""
        if self._service is None:
            if not self._credentials:
                self._credentials = self._get_credentials()
            self._service = build("drive", "v3", credentials=self._credentials)
        return self._service
    
    def _get_credentials(self) -> Credentials:
        """Get Google OAuth2 credentials.
        
        Returns:
            Credentials for Google Drive API
            
        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            credentials = None
            
            # Check for stored credentials
            if hasattr(settings, "GOOGLE_TOKEN_PATH"):
                token_path = Path(settings.GOOGLE_TOKEN_PATH)
                if token_path.exists():
                    credentials = Credentials.from_authorized_user_info(
                        eval(token_path.read_text()),
                        SCOPES
                    )
            
            # If no valid credentials, try to refresh or get new ones
            if not credentials or not credentials.valid:
                if credentials and credentials.expired and credentials.refresh_token:
                    credentials.refresh(Request())
                elif hasattr(settings, "GOOGLE_CREDENTIALS_PATH"):
                    # Use service account or OAuth flow
                    creds_path = Path(settings.GOOGLE_CREDENTIALS_PATH)
                    if creds_path.exists():
                        flow = InstalledAppFlow.from_client_secrets_file(
                            str(creds_path), SCOPES
                        )
                        credentials = flow.run_local_server(port=0)
            
            if not credentials:
                raise AuthenticationError(
                    "No valid Google credentials available",
                    details={"has_token": hasattr(settings, "GOOGLE_TOKEN_PATH")}
                )
            
            return credentials
            
        except HttpError as e:
            raise AuthenticationError(
                f"Failed to authenticate with Google Drive: {e}",
                details={"error": str(e)}
            )
        except Exception as e:
            raise AuthenticationError(
                f"Authentication error: {str(e)}",
                details={"error": str(e)}
            )
    
    def _handle_http_error(self, error: HttpError) -> None:
        """Handle Google Drive API HTTP errors.
        
        Args:
            error: HttpError from Google API
            
        Raises:
            Appropriate GoogleDriveStorageError subclass
        """
        error_code = error.resp.status
        
        if error_code == 401:
            raise AuthenticationError("Authentication required", details={"error": str(error)})
        elif error_code == 403:
            if "rateLimitExceeded" in str(error) or "userRateLimitExceeded" in str(error):
                raise RateLimitError("API rate limit exceeded", details={"error": str(error)})
            raise PermissionError("Access denied", details={"error": str(error)})
        elif error_code == 404:
            raise NotFoundError("Resource not found", details={"error": str(error)})
        elif error_code == 507:
            raise QuotaExceededError("Storage quota exceeded", details={"error": str(error)})
        else:
            raise GoogleDriveStorageError(
                f"Google Drive API error: {error}",
                details={"status": error_code, "error": str(error)}
            )
    
    def upload_file(
        self,
        file_content: BinaryIO,
        file_name: str,
        mime_type: str = "application/octet-stream",
        folder_id: Optional[str] = None,
        parent_folder_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload a file to Google Drive.
        
        Args:
            file_content: File-like object to upload
            file_name: Name of the file
            mime_type: MIME type of the file
            folder_id: ID of the folder to upload to (deprecated, use parent_folder_id)
            parent_folder_id: ID of the parent folder
            
        Returns:
            Dict with file metadata
            
        Raises:
            upload fails
        UploadError: If """
        try:
            # Determine parent folder
            parents = []
            if parent_folder_id:
                parents.append(parent_folder_id)
            elif folder_id:  # Backward compatibility
                parents.append(folder_id)
            
            # Prepare metadata
            file_metadata = {
                "name": file_name,
                "parents": parents if parents else None,
            }
            
            # Create media upload object
            media = MediaIoBaseUpload(
                file_content,
                mimetype=mime_type,
                resumable=True,
            )
            
            # Upload file
            result = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id,name,mimeType,webViewLink,thumbnailLink,createdTime,modifiedTime",
            ).execute()
            
            logger.info(f"Uploaded file: {result.get('name')} (ID: {result.get('id')})")
            return result
            
        except HttpError as e:
            self._handle_http_error(e)
            raise UploadError(f"Failed to upload file: {str(e)}")
        except Exception as e:
            raise UploadError(f"Upload failed: {str(e)}")
    
    def download_file(
        self,
        file_id: str,
        destination: Optional[BinaryIO] = None,
    ) -> bytes:
        """Download a file from Google Drive.
        
        Args:
            file_id: ID of the file to download
            destination: Optional file-like object to write to
            
        Returns:
            File content as bytes if destination is None
            
        Raises:
            DownloadError: If download fails
        """
        try:
            if destination is None:
                destination = io.BytesIO()
            
            request = self.service.files().get_media(fileId=file_id)
            downloader = MediaIoBaseDownload(destination, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    logger.debug(f"Download progress: {int(status.progress() * 100)}%")
            
            destination.seek(0)
            return destination.getvalue() if isinstance(destination, io.BytesIO) else destination
            
        except HttpError as e:
            self._handle_http_error(e)
            raise DownloadError(f"Failed to download file: {str(e)}")
        except Exception as e:
            raise DownloadError(f"Download failed: {str(e)}")
    
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get metadata for a file.
        
        Args:
            file_id: ID of the file
            
        Returns:
            Dict with file metadata
            
        Raises:
            NotFoundError: If file doesn't exist
        """
        try:
            result = self.service.files().get(
                fileId=file_id,
                fields="id,name,mimeType,size,webViewLink,thumbnailLink,createdTime,modifiedTime,parents",
            ).execute()
            return result
        except HttpError as e:
            self._handle_http_error(e)
            raise
    
    def list_files(
        self,
        folder_id: Optional[str] = None,
        mime_type: Optional[str] = None,
        query: Optional[str] = None,
        page_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """List files in Google Drive.
        
        Args:
            folder_id: ID of folder to list (optional)
            mime_type: Filter by MIME type
            query: Custom query string
            page_size: Number of results per page
            
        Returns:
            List of file metadata dicts
        """
        try:
            # Build query
            conditions = []
            if folder_id:
                conditions.append(f"'{folder_id}' in parents")
            if mime_type:
                conditions.append(f"mimeType='{mime_type}'")
            if query:
                conditions.append(query)
            
            query_str = " and ".join(conditions) if conditions else ""
            
            results = []
            page_token = None
            
            while True:
                response = self.service.files().list(
                    q=query_str,
                    pageSize=page_size,
                    fields="nextPageToken,files(id,name,mimeType,size,webViewLink,thumbnailLink,createdTime,modifiedTime)",
                    pageToken=page_token,
                ).execute()
                
                results.extend(response.get("files", []))
                page_token = response.get("nextPageToken")
                
                if not page_token:
                    break
            
            return results
            
        except HttpError as e:
            self._handle_http_error(e)
            raise
    
    def create_folder(
        self,
        name: str,
        parent_folder_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a folder in Google Drive.
        
        Args:
            name: Name of the folder
            parent_folder_id: ID of parent folder (optional)
            
        Returns:
            Dict with folder metadata
        """
        try:
            folder_metadata = {
                "name": name,
                "mimeType": "application/vnd.google-apps.folder",
            }
            
            if parent_folder_id:
                folder_metadata["parents"] = [parent_folder_id]
            
            result = self.service.files().create(
                body=folder_metadata,
                fields="id,name,mimeType,webViewLink",
            ).execute()
            
            logger.info(f"Created folder: {result.get('name')} (ID: {result.get('id')})")
            return result
            
        except HttpError as e:
            self._handle_http_error(e)
            raise
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a file or folder.
        
        Args:
            file_id: ID of the file to delete
            
        Returns:
            True if successful
            
        Raises:
            NotFoundError: If file doesn't exist
        """
        try:
            self.service.files().delete(fileId=file_id).execute()
            logger.info(f"Deleted file: {file_id}")
            return True
        except HttpError as e:
            self._handle_http_error(e)
            raise
    
    def share_file(
        self,
        file_id: str,
        email: str,
        role: str = "reader",
    ) -> Dict[str, Any]:
        """Share a file with another user.
        
        Args:
            file_id: ID of the file Email address to share with
           
            email: role: Role to grant (reader, writer, commenter)
            
        Returns:
            Dict with permission details
        """
        try:
            permission = {
                "type": "user",
                "role": role,
                "emailAddress": email,
            }
            
            result = self.service.permissions().create(
                fileId=file_id,
                body=permission,
                fields="id,type,role,emailAddress",
            ).execute()
            
            logger.info(f"Shared file {file_id} with {email} as {role}")
            return result
            
        except HttpError as e:
            self._handle_http_error(e)
            raise
    
    def get_storage_quota(self) -> Dict[str, Any]:
        """Get storage quota information.
        
        Returns:
            Dict with quota information
        """
        try:
            about = self.service.about().get(fields="storageQuota,user").execute()
            return about.get("storageQuota", {})
        except HttpError as e:
            self._handle_http_error(e)
            raise


# Singleton instance
_drive_storage: Optional[GoogleDriveStorage] = None


def get_drive_storage() -> GoogleDriveStorage:
    """Get or create Google Drive storage singleton."""
    global _drive_storage
    if _drive_storage is None:
        _drive_storage = GoogleDriveStorage()
    return _drive_storage
