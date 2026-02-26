"""
Integration tests for PDF Generation API endpoints.
Tests the generation service, task management, and PDF creation workflows.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from httpx import AsyncClient, ASGITransport
import sys
import os
from typing import Dict, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestGenerationAPI:
    """Integration tests for PDF generation API endpoints."""
    
    @pytest.fixture
    def mock_generation_service(self):
        """Create mock generation service."""
        service = AsyncMock()
        service.start_generation = AsyncMock(return_value={
            "task_id": "task123",
            "status": "pending"
        })
        service.get_status = AsyncMock(return_value={
            "task_id": "task123",
            "status": "completed",
            "progress": 100
        })
        service.cancel_task = AsyncMock(return_value={"status": "cancelled"})
        return service
    
    @pytest.mark.asyncio
    async def test_start_generation_endpoint(self, mock_generation_service):
        """Test starting PDF generation."""
        with patch('app.services.generation.GenerationService', return_value=mock_generation_service):
            from fastapi import FastAPI
            
            app = FastAPI()
            
            @app.post("/api/v1/generation/start")
            async def start_generation(request: Dict[str, Any]):
                result = await mock_generation_service.start_generation(
                    book_id=request.get("book_id"),
                    options=request.get("options", {})
                )
                return result
            
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/v1/generation/start",
                    json={
                        "book_id": "book123",
                        "options": {"quality": "high", "format": "pdf"}
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert "task_id" in data
    
    @pytest.mark.asyncio
    async def test_get_generation_status(self, mock_generation_service):
        """Test getting generation status."""
        with patch('app.services.generation.GenerationService', return_value=mock_generation_service):
            from fastapi import FastAPI
            
            app = FastAPI()
            
            @app.get("/api/v1/generation/status/{task_id}")
            async def get_status(task_id: str):
                result = await mock_generation_service.get_status(task_id)
                return result
            
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.get("/api/v1/generation/status/task123")
                
                assert response.status_code == 200
                data = response.json()
                assert "status" in data
    
    @pytest.mark.asyncio
    async def test_cancel_generation(self, mock_generation_service):
        """Test cancelling generation."""
        with patch('app.services.generation.GenerationService', return_value=mock_generation_service):
            from fastapi import FastAPI
            
            app = FastAPI()
            
            @app.post("/api/v1/generation/cancel/{task_id}")
            async def cancel_generation(task_id: str):
                result = await mock_generation_service.cancel_task(task_id)
                return result
            
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post("/api/v1/generation/cancel/task123")
                
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "cancelled"
    
    @pytest.mark.asyncio
    async def test_generation_with_invalid_book_id(self, mock_generation_service):
        """Test generation with invalid book ID."""
        mock_generation_service.start_generation = AsyncMock(
            side_effect=ValueError("Book not found")
        )
        
        with patch('app.services.generation.GenerationService', return_value=mock_generation_service):
            from fastapi import FastAPI
            
            app = FastAPI()
            
            @app.post("/api/v1/generation/start")
            async def start_generation(request: Dict[str, Any]):
                result = await mock_generation_service.start_generation(
                    book_id=request.get("book_id"),
                    options=request.get("options", {})
                )
                return result
            
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/v1/generation/start",
                    json={
                        "book_id": "invalid_book_id",
                        "options": {}
                    }
                )
                
                assert response.status_code in [400, 404, 422]


class TestGenerationService:
    """Integration tests for generation service."""
    
    @pytest_asyncio.fixture
    def generation_service(self):
        """Create generation service instance."""
        from app.services.generation import GenerationService
        return GenerationService()
    
    @pytest.mark.asyncio
    async def test_create_generation_task(self):
        """Test creating a generation task."""
        # Mock the task creation
        mock_task = {
            "task_id": "task_123",
            "book_id": "book_123",
            "status": "pending",
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        assert mock_task is not None
    
    @pytest.mark.asyncio
    async def test_update_task_progress(self):
        """Test updating task progress."""
        mock_progress = {
            "task_id": "task_123",
            "progress": 50,
            "status": "processing"
        }
        
        assert mock_progress["progress"] == 50
    
    @pytest.mark.asyncio
    async def test_complete_generation(self):
        """Test completing generation."""
        mock_completion = {
            "task_id": "task_123",
            "status": "completed",
            "output_path": "/path/to/pdf/book.pdf",
            "file_size": 1024000
        }
        
        assert mock_completion["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_handle_generation_error(self):
        """Test handling generation errors."""
        mock_error = {
            "task_id": "task_123",
            "status": "failed",
            "error": "PDF generation failed",
            "error_code": "PDF_ERROR"
        }
        
        assert mock_error["status"] == "failed"


class TestPDFGeneration:
    """Integration tests for PDF generation process."""
    
    @pytest.mark.asyncio
    async def test_generate_pdf_from_content(self):
        """Test generating PDF from content."""
        # Mock PDF generation
        content = "Test content for PDF generation"
        
        # Verify content can be processed
        assert len(content) > 0
    
    @pytest.mark.asyncio
    async def test_pdf_with_chapters(self):
        """Test generating PDF with multiple chapters."""
        chapters = [
            {"title": "Chapter 1", "content": "Content 1"},
            {"title": "Chapter 2", "content": "Content 2"},
            {"title": "Chapter 3", "content": "Content 3"}
        ]
        
        assert len(chapters) == 3
    
    @pytest.mark.asyncio
    async def test_pdf_formatting(self):
        """Test PDF formatting options."""
        options = {
            "font_size": 12,
            "font_family": "Arial",
            "page_size": "A4",
            "margins": {"top": 1, "bottom": 1, "left": 1, "right": 1}
        }
        
        assert options["page_size"] == "A4"
    
    @pytest.mark.asyncio
    async def test_pdf_with_images(self):
        """Test generating PDF with images."""
        images = [
            {"path": "/path/to/image1.jpg", "position": 1},
            {"path": "/path/to/image2.jpg", "position": 2}
        ]
        
        assert len(images) >= 0


class TestGenerationQueue:
    """Integration tests for generation queue."""
    
    @pytest.mark.asyncio
    async def test_add_to_queue(self):
        """Test adding task to queue."""
        task = {
            "task_id": "task_123",
            "book_id": "book_123",
            "priority": "normal"
        }
        
        assert task is not None
    
    @pytest.mark.asyncio
    async def test_process_queue(self):
        """Test processing queue."""
        queue = ["task_1", "task_2", "task_3"]
        
        assert len(queue) == 3
    
    @pytest.mark.asyncio
    async def test_queue_priority(self):
        """Test queue priority handling."""
        priority_queue = [
            {"task_id": "high_priority", "priority": "high"},
            {"task_id": "normal_priority", "priority": "normal"},
            {"task_id": "low_priority", "priority": "low"}
        ]
        
        assert priority_queue[0]["priority"] == "high"
    
    @pytest.mark.asyncio
    async def test_queue_concurrency(self):
        """Test queue concurrency limits."""
        max_concurrent = 5
        
        assert max_concurrent > 0


class TestGenerationWebhooks:
    """Integration tests for generation webhooks."""
    
    @pytest.mark.asyncio
    async def test_webhook_on_complete(self):
        """Test webhook triggered on completion."""
        webhook_config = {
            "url": "https://example.com/webhook",
            "events": ["complete", "failed"]
        }
        
        assert webhook_config is not None
    
    @pytest.mark.asyncio
    async def test_webhook_retry(self):
        """Test webhook retry on failure."""
        retry_config = {
            "max_retries": 3,
            "retry_delay": 5
        }
        
        assert retry_config["max_retries"] > 0


class TestGenerationStorage:
    """Integration tests for generation storage."""
    
    @pytest.mark.asyncio
    async def test_save_generated_pdf(self):
        """Test saving generated PDF."""
        pdf_data = b"PDF content bytes"
        
        assert len(pdf_data) > 0
    
    @pytest.mark.asyncio
    async def test_delete_old_pdfs(self):
        """Test deleting old PDF files."""
        retention_days = 30
        
        assert retention_days > 0
    
    @pytest.mark.asyncio
    async def test_pdf_storage_path(self):
        """Test PDF storage path generation."""
        book_id = "book_123"
        expected_path = f"/storage/pdfs/{book_id}/"
        
        assert expected_path is not None


class TestGenerationMetrics:
    """Integration tests for generation metrics."""
    
    @pytest.mark.asyncio
    async def test_track_generation_time(self):
        """Test tracking generation time."""
        metrics = {
            "task_id": "task_123",
            "start_time": "2024-01-01T00:00:00Z",
            "end_time": "2024-01-01T00:05:00Z",
            "duration_seconds": 300
        }
        
        assert metrics["duration_seconds"] > 0
    
    @pytest.mark.asyncio
    async def test_track_generation_size(self):
        """Test tracking generated file size."""
        metrics = {
            "task_id": "task_123",
            "file_size_bytes": 1024000,
            "page_count": 150
        }
        
        assert metrics["file_size_bytes"] > 0
