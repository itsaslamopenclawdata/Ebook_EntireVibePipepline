"""
Unit tests for ebook endpoints.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from typing import Optional


class TestEbookService:
    """Test cases for ebook service."""
    
    @pytest.fixture
    def mock_book_repository(self):
        """Create mock book repository."""
        return Mock()
    
    @pytest.fixture
    def ebook_service(self, mock_book_repository):
        """Create ebook service instance."""
        from app.services.ebook import EbookService
        return EbookService(book_repository=mock_book_repository)
    
    @pytest.mark.asyncio
    async def test_create_book(self, ebook_service, mock_book_repository):
        """Test book creation."""
        mock_book = Mock()
        mock_book.id = "book123"
        mock_book.title = "Test Book"
        mock_book.description = "Test description"
        mock_book.user_id = "user123"
        
        mock_book_repository.create = AsyncMock(return_value=mock_book)
        
        book = await ebook_service.create_book(
            title="Test Book",
            description="Test description",
            user_id="user123"
        )
        
        assert book is not None
        assert book.title == "Test Book"
        mock_book_repository.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_book_by_id(self, ebook_service, mock_book_repository):
        """Test getting book by ID."""
        mock_book = Mock()
        mock_book.id = "book123"
        mock_book.title = "Test Book"
        
        mock_book_repository.get_by_id = AsyncMock(return_value=mock_book)
        
        book = await ebook_service.get_book("book123")
        
        assert book is not None
        assert book.id == "book123"
    
    @pytest.mark.asyncio
    async def test_get_book_by_id_not_found(self, ebook_service, mock_book_repository):
        """Test getting non-existent book."""
        mock_book_repository.get_by_id = AsyncMock(return_value=None)
        
        book = await ebook_service.get_book("nonexistent")
        
        assert book is None
    
    @pytest.mark.asyncio
    async def test_list_user_books(self, ebook_service, mock_book_repository):
        """Test listing user books."""
        mock_books = [
            Mock(id="book1", title="Book 1"),
            Mock(id="book2", title="Book 2"),
        ]
        
        mock_book_repository.list_by_user = AsyncMock(return_value=mock_books)
        
        books = await ebook_service.list_books("user123")
        
        assert len(books) == 2
        assert books[0].title == "Book 1"
    
    @pytest.mark.asyncio
    async def test_update_book(self, ebook_service, mock_book_repository):
        """Test book update."""
        mock_book = Mock()
        mock_book.id = "book123"
        mock_book.title = "Updated Title"
        
        mock_book_repository.update = AsyncMock(return_value=mock_book)
        
        book = await ebook_service.update_book(
            "book123",
            title="Updated Title"
        )
        
        assert book.title == "Updated Title"
        mock_book_repository.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_book(self, ebook_service, mock_book_repository):
        """Test book deletion."""
        mock_book_repository.delete = AsyncMock(return_value=True)
        
        result = await ebook_service.delete_book("book123")
        
        assert result is True
        mock_book_repository.delete.assert_called_once_with("book123")


class TestChapterService:
    """Test cases for chapter service."""
    
    @pytest.fixture
    def chapter_service(self):
        """Create chapter service instance."""
        from app.services.ebook import ChapterService
        return ChapterService()
    
    @pytest.mark.asyncio
    async def test_create_chapter(self, chapter_service):
        """Test chapter creation."""
        chapter = await chapter_service.create_chapter(
            book_id="book123",
            title="Chapter 1",
            order=1,
            user_id="user123"
        )
        
        assert chapter is not None
        assert chapter.title == "Chapter 1"
        assert chapter.order == 1
    
    @pytest.mark.asyncio
    async def test_get_chapters_by_book(self, chapter_service):
        """Test getting chapters by book."""
        chapters = await chapter_service.get_chapters_by_book("book123")
        
        assert isinstance(chapters, list)
    
    @pytest.mark.asyncio
    async def test_update_chapter_content(self, chapter_service):
        """Test updating chapter content."""
        chapter = await chapter_service.update_content(
            "chapter123",
            content="Updated content here"
        )
        
        assert chapter.content == "Updated content here"


class TestPDFGeneration:
    """Test cases for PDF generation."""
    
    @pytest.fixture
    def pdf_service(self):
        """Create PDF service instance."""
        from app.services.pdf import PDFGenerationService
        return PDFGenerationService()
    
    @pytest.mark.asyncio
    async def test_generate_pdf(self, pdf_service):
        """Test PDF generation."""
        result = await pdf_service.generate_pdf(
            book_id="book123",
            options={"quality": "high"}
        )
        
        assert result is not None
        assert "pdf_url" in result or "task_id" in result
    
    @pytest.mark.asyncio
    async def test_get_generation_status(self, pdf_service):
        """Test getting generation status."""
        status = await pdf_service.get_status("task123")
        
        assert status is not None
        assert "status" in status
    
    @pytest.mark.asyncio
    async def test_cancel_generation(self, pdf_service):
        """Test cancelling PDF generation."""
        result = await pdf_service.cancel("task123")
        
        assert result is True


class TestEbookValidation:
    """Test cases for ebook validation."""
    
    def test_validate_book_title(self):
        """Test book title validation."""
        from app.schemas.ebook import BookCreate
        
        # Valid title
        book = BookCreate(title="Valid Title", description="Description")
        assert book.title == "Valid Title"
        
        # Test empty title handled by schema
        with pytest.raises(Exception):
            BookCreate(title="", description="Description")
    
    def test_validate_chapter_order(self):
        """Test chapter order validation."""
        from app.schemas.ebook import ChapterCreate
        
        # Valid order
        chapter = ChapterCreate(title="Chapter 1", order=1)
        assert chapter.order == 1
        
        # Negative order should fail
        with pytest.raises(Exception):
            ChapterCreate(title="Chapter", order=-1)
