"""Storage service - unified interface for all storage backends."""
import io
import logging
from typing import Optional, List, Dict, Any, BinaryIO
from datetime import datetime

from app.services.storage import (
    GoogleDriveStorage,
    get_drive_storage,
    GoogleDriveStorageError,
    UploadError,
    DownloadError,
    NotFoundError,
)

logger = logging.getLogger(__name__)


class StorageService:
    """Unified storage service supporting multiple backends."""
    
    def __init__(self, backend: str = "google_drive"):
        """Initialize storage service.
        
        Args:
            backend: Storage backend to use ("google_drive" currently supported)
        """
        self.backend = backend
        self._drive_storage: Optional[GoogleDriveStorage] = None
    
    @property
    def drive_storage(self) -> GoogleDriveStorage:
        """Get Google Drive storage instance."""
        if self._drive_storage is None:
            self._drive_storage = get_drive_storage()
        return self._drive_storage
    
    # ========== File Operations ==========
    
    async def upload_ebook(
        self,
        content: bytes,
        file_name: str,
        user_id: str,
        folder_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload an ebook to storage.
        
        Args:
            content: File content as bytes
            file_name: Name of the file
            user_id: ID of the user uploading the file
            folder_id: Optional folder ID to upload to
            
        Returns:
            Dict with file metadata including file_id and download URL
        """
        try:
            file_obj = io.BytesIO(content)
            
            if self.backend == "google_drive":
                # Determine folder path
                target_folder = folder_id or f"ebooks_{user_id}"
                
                # Try to find or create user folder
                try:
                    folder = await self._get_or_create_folder(target_folder)
                    parent_id = folder.get("id")
                except Exception:
                    parent_id = None
                
                result = self.drive_storage.upload_file(
                    file_content=file_obj,
                    file_name=file_name,
                    mime_type="application/pdf",
                    parent_folder_id=parent_id,
                )
                
                return {
                    "file_id": result.get("id"),
                    "file_name": result.get("name"),
                    "url": result.get("webViewLink"),
                    "created_at": result.get("createdTime"),
                    "modified_at": result.get("modifiedTime"),
                }
            else:
                raise ValueError(f"Unsupported storage backend: {self.backend}")
                
        except GoogleDriveStorageError as e:
            logger.error(f"Failed to upload ebook: {e}")
            raise UploadError(f"Failed to upload ebook: {str(e)}")
    
    async def download_ebook(
        self,
        file_id: str,
    ) -> bytes:
        """Download an ebook from storage.
        
        Args:
            file_id: ID of the file to download
            
        Returns:
            File content as bytes
        """
        try:
            if self.backend == "google_drive":
                content = self.drive_storage.download_file(file_id)
                return content
            else:
                raise ValueError(f"Unsupported storage backend: {self.backend}")
                
        except GoogleDriveStorageError as e:
            logger.error(f"Failed to download ebook: {e}")
            raise DownloadError(f"Failed to download ebook: {str(e)}")
    
    async def get_file_info(
        self,
        file_id: str,
    ) -> Dict[str, Any]:
        """Get file information.
        
        Args:
            file_id: ID of the file
            
        Returns:
            Dict with file metadata
        """
        if self.backend == "google_drive":
            return self.drive_storage.get_file_metadata(file_id)
        else:
            raise ValueError(f"Unsupported storage backend: {self.backend}")
    
    async def delete_file(
        self,
        file_id: str,
    ) -> bool:
        """Delete a file.
        
        Args:
            file_id: ID of the file to delete
            
        Returns:
            True if successful
        """
        if self.backend == "google_drive":
            return self.drive_storage.delete_file(file_id)
        else:
            raise ValueError(f"Unsupported storage backend: {self.backend}")
    
    async def list_files(
        self,
        folder_id: Optional[str] = None,
        mime_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List files in storage.
        
        Args:
            folder_id: Optional folder ID to list
            mime_type: Optional MIME type filter
            
        Returns:
            List of file metadata dicts
        """
        if self.backend == "google_drive":
            return self.drive_storage.list_files(
                folder_id=folder_id,
                mime_type=mime_type,
            )
        else:
            raise ValueError(f"Unsupported storage backend: {self.backend}")
    
    # ========== Folder Operations ==========
    
    async def create_folder(
        self,
        name: str,
        parent_folder_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a folder.
        
        Args:
            name: Name of the folder
            parent_folder_id: Optional parent folder ID
            
        Returns:
            Dict with folder metadata
        """
        if self.backend == "google_drive":
            return self.drive_storage.create_folder(
                name=name,
                parent_folder_id=parent_folder_id,
            )
        else:
            raise ValueError(f"Unsupported storage backend: {self.backend}")
    
    async def _get_or_create_folder(
        self,
        name: str,
        parent_folder_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get existing folder or create new one.
        
        Args:
            name: Name of the folder
            parent_folder_id: Optional parent folder ID
            
        Returns:
            Dict with folder metadata
        """
        if self.backend == "google_drive":
            # Try to find existing folder
            query = f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
            if parent_folder_id:
                query += f" and '{parent_folder_id}' in parents"
            
            results = self.drive_storage.list_files(query=query)
            
            if results:
                return results[0]
            
            # Create new folder
            return self.drive_storage.create_folder(
                name=name,
                parent_folder_id=parent_folder_id,
            )
        else:
            raise ValueError(f"Unsupported storage backend: {self.backend}")
    
    # ========== Sharing ==========
    
    async def share_file(
        self,
        file_id: str,
        email: str,
        role: str = "reader",
    ) -> Dict[str, Any]:
        """Share a file with another user.
        
        Args:
            file_id: ID of the file
            email: Email address to share with
            role: Role to grant (reader, writer, commenter)
            
        Returns:
            Dict with permission details
        """
        if self.backend == "google_drive":
            return self.drive_storage.share_file(
                file_id=file_id,
                email=email,
                role=role,
            )
        else:
            raise ValueError(f"Unsupported storage backend: {self.backend}")
    
    # ========== Utilities ==========
    
    async def get_storage_info(self) -> Dict[str, Any]:
        """Get storage quota information.
        
        Returns:
            Dict with storage quota info
        """
        if self.backend == "google_drive":
            return self.drive_storage.get_storage_quota()
        else:
            raise ValueError(f"Unsupported storage backend: {self.backend}")


# Singleton instance
_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """Get or create storage service singleton."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
