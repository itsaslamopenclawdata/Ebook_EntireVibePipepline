"""
Integration tests for external service integrations.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestAnthropicClient:
    """Test Anthropic API client integration."""
    
    @pytest.fixture
    def anthropic_client(self):
        """Create Anthropic client."""
        from app.services.ai.anthropic import AnthropicClient
        return AnthropicClient(api_key="test-key")
    
    @pytest.mark.asyncio
    async def test_generate_content(self, anthropic_client):
        """Test content generation with Anthropic."""
        # Mock the API call
        with patch.object(anthropic_client, 'generate', new_callable=AsyncMock) as mock:
            mock.return_value = Mock(
                content="Generated content",
                model="claude-3-opus",
                usage={"input_tokens": 100, "output_tokens": 200}
            )
            
            result = await anthropic_client.generate(
                prompt="Write a story",
                model="claude-3-opus",
                max_tokens=1000
            )
            
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_generate_outline(self, anthropic_client):
        """Test outline generation."""
        with patch.object(anthropic_client, 'generate_outline', new_callable=AsyncMock) as mock:
            mock.return_value = {
                "title": "Book Title",
                "chapters": [
                    {"title": "Chapter 1", "sections": []}
                ]
            }
            
            result = await anthropic_client.generate_outline(
                topic="Python Programming",
                num_chapters=5
            )
            
            assert result is not None
    
    def test_client_initialization(self, anthropic_client):
        """Test client initializes correctly."""
        assert anthropic_client.api_key == "test-key"


class TestOpenAIClient:
    """Test OpenAI API client integration."""
    
    @pytest.fixture
    def openai_client(self):
        """Create OpenAI client."""
        from app.services.ai.openai import OpenAIClient
        return OpenAIClient(api_key="test-key")
    
    @pytest.mark.asyncio
    async def test_generate_content(self, openai_client):
        """Test content generation with OpenAI."""
        with patch.object(openai_client, 'generate', new_callable=AsyncMock) as mock:
            mock.return_value = Mock(
                content="Generated content",
                model="gpt-4",
                usage={"prompt_tokens": 100, "completion_tokens": 200}
            )
            
            result = await openai_client.generate(
                prompt="Write a story",
                model="gpt-4",
                max_tokens=1000
            )
            
            assert result is not None


class TestGoogleDriveService:
    """Test Google Drive integration."""
    
    @pytest.fixture
    def google_drive_service(self):
        """Create Google Drive service."""
        from app.services.storage.google_drive import GoogleDriveService
        return GoogleDriveService()
    
    @pytest.mark.asyncio
    async def test_upload_file(self, google_drive_service):
        """Test file upload to Google Drive."""
        with patch.object(google_drive_service, 'upload', new_callable=AsyncMock) as mock:
            mock.return_value = "https://drive.google.com/file/id123"
            
            result = await google_drive_service.upload(
                file_path="/tmp/test.pdf",
                folder_id="folder123"
            )
            
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_download_file(self, google_drive_service):
        """Test file download from Google Drive."""
        with patch.object(google_drive_service, 'download', new_callable=AsyncMock) as mock:
            mock.return_value = b"file content"
            
            result = await google_drive_service.download("file_id_123")
            
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_list_files(self, google_drive_service):
        """Test listing files in Google Drive."""
        with patch.object(google_drive_service, 'list_files', new_callable=AsyncMock) as mock:
            mock.return_value = [
                {"id": "file1", "name": "file1.pdf"},
                {"id": "file2", "name": "file2.pdf"}
            ]
            
            result = await google_drive_service.list_files("folder123")
            
            assert len(result) == 2


class TestPDFService:
    """Test PDF generation service integration."""
    
    @pytest.fixture
    def pdf_service(self):
        """Create PDF service."""
        from app.services.pdf import PDFGenerationService
        return PDFGenerationService()
    
    @pytest.mark.asyncio
    async def test_generate_pdf(self, pdf_service):
        """Test PDF generation."""
        with patch.object(pdf_service, 'generate', new_callable=AsyncMock) as mock:
            mock.return_value = {
                "task_id": "task123",
                "status": "processing"
            }
            
            result = await pdf_service.generate(
                book_id="book123",
                options={"quality": "high"}
            )
            
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_get_pdf_status(self, pdf_service):
        """Test getting PDF generation status."""
        with patch.object(pdf_service, 'get_status', new_callable=AsyncMock) as mock:
            mock.return_value = {
                "task_id": "task123",
                "status": "completed",
                "pdf_url": "https://example.com/book.pdf"
            }
            
            result = await pdf_service.get_status("task123")
            
            assert result["status"] == "completed"


class TestCeleryTasks:
    """Test Celery task integration."""
    
    @pytest.mark.asyncio
    async def test_generate_pdf_task(self):
        """Test PDF generation Celery task."""
        # Mock Celery task
        mock_task = AsyncMock()
        mock_task.id = "task123"
        mock_task.status = "PENDING"
        
        with patch('app.worker.generate_pdf_task') as mock:
            mock.apply_async.return_value = mock_task
            
            result = mock.apply_async(args=["book123"], queue="pdf_generation")
            
            assert result.id == "task123"
    
    @pytest.mark.asyncio
    async def test_cleanup_task(self):
        """Test cleanup Celery task."""
        mock_task = AsyncMock()
        
        with patch('app.worker.cleanup_old_files') as mock:
            mock.apply_async.return_value = mock_task
            
            result = mock.apply_async()
            
            assert result is not None


class TestWebSocketService:
    """Test WebSocket service integration."""
    
    @pytest.fixture
    def websocket_manager(self):
        """Create WebSocket manager."""
        from app.services.websocket import ConnectionManager
        return ConnectionManager()
    
    @pytest.mark.asyncio
    async def test_connect(self, websocket_manager):
        """Test WebSocket connection."""
        mock_websocket = Mock()
        mock_websocket.send = AsyncMock()
        
        # Should not raise error
        await websocket_manager.connect(mock_websocket, "user123")
    
    @pytest.mark.asyncio
    async def test_disconnect(self, websocket_manager):
        """Test WebSocket disconnection."""
        # Should not raise error
        await websocket_manager.disconnect("user123")
    
    @pytest.mark.asyncio
    async def test_send_personal_message(self, websocket_manager):
        """Test sending personal message."""
        mock_websocket = Mock()
        mock_websocket.send = AsyncMock()
        
        await websocket_manager.connect(mock_websocket, "user123")
        await websocket_manager.send_personal_message("Hello", "user123")


class TestRedisCache:
    """Test Redis caching integration."""
    
    @pytest.fixture
    def cache_service(self):
        """Create cache service."""
        from app.services.cache import CacheService
        return CacheService()
    
    @pytest.mark.asyncio
    async def test_set_cache(self, cache_service):
        """Test setting cache value."""
        with patch.object(cache_service, 'set', new_callable=AsyncMock) as mock:
            mock.return_value = True
            
            result = await cache_service.set("key", "value", ttl=60)
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_get_cache(self, cache_service):
        """Test getting cache value."""
        with patch.object(cache_service, 'get', new_callable=AsyncMock) as mock:
            mock.return_value = "value"
            
            result = await cache_service.get("key")
            
            assert result == "value"
    
    @pytest.mark.asyncio
    async def test_delete_cache(self, cache_service):
        """Test deleting cache value."""
        with patch.object(cache_service, 'delete', new_callable=AsyncMock) as mock:
            mock.return_value = True
            
            result = await cache_service.delete("key")
            
            assert result is True


class TestExternalAPIErrors:
    """Test error handling for external API failures."""
    
    @pytest.mark.asyncio
    async def test_anthropic_rate_limit(self):
        """Test handling rate limit from Anthropic."""
        from app.services.ai.anthropic import AnthropicRateLimitError
        
        with pytest.raises(AnthropicRateLimitError):
            raise AnthropicRateLimitError("Rate limit exceeded")
    
    @pytest.mark.asyncio
    async def test_google_drive_auth_error(self):
        """Test handling Google Drive auth error."""
        from app.services.storage.google_drive import GoogleDriveAuthError
        
        with pytest.raises(GoogleDriveAuthError):
            raise GoogleDriveAuthError("Authentication failed")
