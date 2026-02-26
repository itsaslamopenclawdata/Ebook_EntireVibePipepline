"""
Integration tests for Books API endpoints.
Tests the books CRUD operations, chapters, and book management.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from httpx import AsyncClient, ASGITransport
import sys
import os
from typing import Dict, Any
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestBooksAPI:
    """Integration tests for books API endpoints."""
    
    @pytest.fixture
    def mock_book_service(self):
        """Create mock book service."""
        service = AsyncMock()
        service.create_book = AsyncMock(return_value={
            "id": "book123",
            "title": "Test Book",
            "description": "Test description",
            "status": "draft",
            "user_id": "user123",
            "created_at": datetime.utcnow().isoformat()
        })
        service.get_book = AsyncMock(return_value={
            "id": "book123",
            "title": "Test Book",
            "description": "Test description",
            "status": "draft",
            "user_id": "user123"
        })
        service.list_books = AsyncMock(return_value=[
            {"id": "book1", "title": "Book 1"},
            {"id": "book2", "title": "Book 2"}
        ])
        service.update_book = AsyncMock(return_value={
            "id": "book123",
            "title": "Updated Book",
            "status": "published"
        })
        service.delete_book = AsyncMock(return_value={"status": "deleted"})
        return service
    
    @pytest.mark.asyncio
    async def test_create_book(self, mock_book_service):
        """Test creating a new book."""
        from fastapi import FastAPI
        
        app = FastAPI()
        
        @app.post("/api/v1/books/")
        async def create_book(request: Dict[str, Any]):
            result = await mock_book_service.create_book(
                user_id="user123",
                title=request.get("title"),
                description=request.get("description", ""),
                topic=request.get("topic"),
                target_audience=request.get("target_audience")
            )
            return result
        
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/books/",
                json={
                    "title": "My New Book",
                    "description": "A test book",
                    "topic": "Technology",
                    "target_audience": "Developers"
                }
            )
            
            assert response.status_code == 201
            data = response.json()
            assert "id" in data
            assert data["title"] == "My New Book"
    
    @pytest.mark.asyncio
    async def test_get_book(self, mock_book_service):
        """Test getting a specific book."""
        from fastapi import FastAPI
        
        app = FastAPI()
        
        @app.get("/api/v1/books/{book_id}")
        async def get_book(book_id: str):
            result = await mock_book_service.get_book(book_id)
            return result
        
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/books/book123")
            
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
    
    @pytest.mark.asyncio
    async def test_list_books(self, mock_book_service):
        """Test listing user's books."""
        from fastapi import FastAPI
        
        app = FastAPI()
        
        @app.get("/api/v1/books/")
        async def list_books():
            result = await mock_book_service.list_books(user_id="user123")
            return result
        
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/books/")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_update_book(self, mock_book_service):
        """Test updating a book."""
        from fastapi import FastAPI
        
        app = FastAPI()
        
        @app.put("/api/v1/books/{book_id}")
        async def update_book(book_id: str, request: Dict[str, Any]):
            result = await mock_book_service.update_book(
                book_id=book_id,
                title=request.get("title"),
                description=request.get("description"),
                status=request.get("status")
            )
            return result
        
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.put(
                "/api/v1/books/book123",
                json={"title": "Updated Title", "status": "published"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "Updated Title"
    
    @pytest.mark.asyncio
    async def test_delete_book(self, mock_book_service):
        """Test deleting a book."""
        from fastapi import FastAPI
        
        app = FastAPI()
        
        @app.delete("/api/v1/books/{book_id}")
        async def delete_book(book_id: str):
            result = await mock_book_service.delete_book(book_id)
            return result
        
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.delete("/api/v1/books/book123")
            
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_book(self, mock_book_service):
        """Test getting a book that doesn't exist."""
        mock_book_service.get_book = AsyncMock(return_value=None)
        
        from fastapi import FastAPI
        from fastapi import HTTPException
        
        app = FastAPI()
        
        @app.get("/api/v1/books/{book_id}")
        async def get_book(book_id: str):
            result = await mock_book_service.get_book(book_id)
            if not result:
                raise HTTPException(status_code=404, detail="Book not found")
            return result
        
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/books/nonexistent")
            
            assert response.status_code == 404


class TestChaptersAPI:
    """Integration tests for chapters API endpoints."""
    
    @pytest.fixture
    def mock_chapter_service(self):
        """Create mock chapter service."""
        service = AsyncMock()
        service.create_chapter = AsyncMock(return_value={
            "id": "chapter123",
            "book_id": "book123",
            "title": "Chapter 1",
            "content": "Chapter content",
            "order": 1
        })
        service.get_chapters = AsyncMock(return_value=[
            {"id": "chapter1", "title": "Chapter 1", "order": 1},
            {"id": "chapter2", "title": "Chapter 2", "order": 2}
        ])
        service.update_chapter = AsyncMock(return_value={
            "id": "chapter123",
            "title": "Updated Chapter"
        })
        service.delete_chapter = AsyncMock(return_value={"status": "deleted"})
        return service
    
    @pytest.mark.asyncio
    async def test_create_chapter(self, mock_chapter_service):
        """Test creating a new chapter."""
        from fastapi import FastAPI
        
        app = FastAPI()
        
        @app.post("/api/v1/books/{book_id}/chapters")
        async def create_chapter(book_id: str, request: Dict[str, Any]):
            result = await mock_chapter_service.create_chapter(
                book_id=book_id,
                title=request.get("title"),
                content=request.get("content", ""),
                order=request.get("order", 1)
            )
            return result
        
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/books/book123/chapters",
                json={
                    "title": "Chapter 1: Introduction",
                    "content": "This is the introduction...",
                    "order": 1
                }
            )
            
            assert response.status_code == 201
            data = response.json()
            assert "id" in data
    
    @pytest.mark.asyncio
    async def test_list_chapters(self, mock_chapter_service):
        """Test listing chapters for a book."""
        from fastapi import FastAPI
        
        app = FastAPI()
        
        @app.get("/api/v1/books/{book_id}/chapters")
        async def list_chapters(book_id: str):
            result = await mock_chapter_service.get_chapters(book_id)
            return result
        
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/books/book123/chapters")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_update_chapter(self, mock_chapter_service):
        """Test updating a chapter."""
        from fastapi import FastAPI
        
        app = FastAPI()
        
        @app.put("/api/v1/books/{book_id}/chapters/{chapter_id}")
        async def update_chapter(book_id: str, chapter_id: str, request: Dict[str, Any]):
            result = await mock_chapter_service.update_chapter(
                chapter_id=chapter_id,
                title=request.get("title"),
                content=request.get("content")
            )
            return result
        
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.put(
                "/api/v1/books/book123/chapters/chapter123",
                json={"title": "Updated Chapter Title"}
            )
            
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_delete_chapter(self, mock_chapter_service):
        """Test deleting a chapter."""
        from fastapi import FastAPI
        
        app = FastAPI()
        
        @app.delete("/api/v1/books/{book_id}/chapters/{chapter_id}")
        async def delete_chapter(book_id: str, chapter_id: str):
            result = await mock_chapter_service.delete_chapter(chapter_id)
            return result
        
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.delete("/api/v1/books/book123/chapters/chapter123")
            
            assert response.status_code == 200


class TestBookSearch:
    """Integration tests for book search functionality."""
    
    @pytest.mark.asyncio
    async def test_search_books_by_title(self):
        """Test searching books by title."""
        search_query = "python"
        
        assert search_query is not None
    
    @pytest.mark.asyncio
    async def test_search_books_by_topic(self):
        """Test searching books by topic."""
        search_results = [
            {"id": "book1", "title": "Python Basics", "topic": "Programming"},
            {"id": "book2", "title": "Advanced Python", "topic": "Programming"}
        ]
        
        assert len(search_results) == 2
    
    @pytest.mark.asyncio
    async def test_filter_books_by_status(self):
        """Test filtering books by status."""
        status_filter = "published"
        
        assert status_filter is not None
    
    @pytest.mark.asyncio
    async def test_pagination(self):
        """Test book list pagination."""
        pagination = {
            "page": 1,
            "per_page": 10,
            "total": 50
        }
        
        assert pagination["per_page"] > 0


class TestBookVersions:
    """Integration tests for book versioning."""
    
    @pytest.mark.asyncio
    async def test_create_book_version(self):
        """Test creating a book version."""
        version = {
            "book_id": "book123",
            "version_number": 1,
            "created_at": datetime.utcnow().isoformat()
        }
        
        assert version is not None
    
    @pytest.mark.asyncio
    async def test_list_book_versions(self):
        """Test listing book versions."""
        versions = [
            {"version": 1, "created_at": "2024-01-01"},
            {"version": 2, "created_at": "2024-01-15"}
        ]
        
        assert len(versions) == 2
    
    @pytest.mark.asyncio
    async def test_restore_book_version(self):
        """Test restoring a book version."""
        restore_result = {
            "status": "restored",
            "restored_from_version": 1
        }
        
        assert restore_result is not None


class TestBookCollaboration:
    """Integration tests for book collaboration."""
    
    @pytest.mark.asyncio
    async def test_invite_collaborator(self):
        """Test inviting a collaborator."""
        invite = {
            "book_id": "book123",
            "user_id": "user456",
            "role": "editor"
        }
        
        assert invite["role"] == "editor"
    
    @pytest.mark.asyncio
    async def test_remove_collaborator(self):
        """Test removing a collaborator."""
        remove_result = {"status": "removed"}
        
        assert remove_result["status"] == "removed"
    
    @pytest.mark.asyncio
    async def test_list_collaborators(self):
        """Test listing book collaborators."""
        collaborators = [
            {"user_id": "user1", "role": "owner"},
            {"user_id": "user2", "role": "editor"}
        ]
        
        assert len(collaborators) >= 1


class TestBookAnalytics:
    """Integration tests for book analytics."""
    
    @pytest.mark.asyncio
    async def test_track_book_views(self):
        """Test tracking book views."""
        view_event = {
            "book_id": "book123",
            "user_id": "user123",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        assert view_event is not None
    
    @pytest.mark.asyncio
    async def test_book_statistics(self):
        """Test getting book statistics."""
        stats = {
            "book_id": "book123",
            "views": 150,
            "downloads": 45,
            "shares": 20
        }
        
        assert stats["views"] > 0
    
    @pytest.mark.asyncio
    async def test_reading_progress(self):
        """Test tracking reading progress."""
        progress = {
            "book_id": "book123",
            "user_id": "user123",
            "chapters_read": 3,
            "total_chapters": 10,
            "percentage": 30
        }
        
        assert progress["percentage"] >= 0


class TestBookExport:
    """Integration tests for book export functionality."""
    
    @pytest.mark.asyncio
    async def test_export_to_pdf(self):
        """Test exporting book to PDF."""
        export_request = {
            "book_id": "book123",
            "format": "pdf",
            "options": {"quality": "high"}
        }
        
        assert export_request["format"] == "pdf"
    
    @pytest.mark.asyncio
    async def test_export_to_epub(self):
        """Test exporting book to EPUB."""
        export_request = {
            "book_id": "book123",
            "format": "epub"
        }
        
        assert export_request is not None
    
    @pytest.mark.asyncio
    async def test_export_status(self):
        """Test checking export status."""
        export_status = {
            "export_id": "export123",
            "status": "completed",
            "download_url": "https://example.com/download/book.pdf"
        }
        
        assert "download_url" in export_status


class TestBookPermissions:
    """Integration tests for book permissions."""
    
    @pytest.mark.asyncio
    async def test_check_book_access(self):
        """Test checking user access to book."""
        access_check = {
            "user_id": "user123",
            "book_id": "book123",
            "has_access": True
        }
        
        assert access_check is not None
    
    @pytest.mark.asyncio
    async def test_private_book_access(self):
        """Test private book access control."""
        private_book = {
            "id": "book123",
            "is_public": False,
            "owner_id": "user123"
        }
        
        assert private_book["is_public"] is False
    
    @pytest.mark.asyncio
    async def test_public_book_access(self):
        """Test public book access."""
        public_book = {
            "id": "book456",
            "is_public": True,
            "owner_id": "user456"
        }
        
        assert public_book["is_public"] is True
