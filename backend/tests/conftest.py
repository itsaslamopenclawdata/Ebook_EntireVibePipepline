"""
Pytest configuration and shared fixtures.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, Mock, MagicMock
from typing import AsyncGenerator
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


# ============================================================================
# Fixtures: Mock Objects
# ============================================================================

@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_user():
    """Create a mock user object."""
    user = Mock()
    user.id = "user123"
    user.email = "test@example.com"
    user.username = "testuser"
    user.full_name = "Test User"
    user.hashed_password = "hashed_password"
    user.is_active = True
    user.is_verified = True
    user.created_at = Mock()
    user.updated_at = Mock()
    return user


@pytest.fixture
def mock_book():
    """Create a mock book object."""
    book = Mock()
    book.id = "book123"
    book.title = "Test Book"
    book.description = "A test book"
    book.user_id = "user123"
    book.status = "draft"
    book.created_at = Mock()
    book.updated_at = Mock()
    return book


@pytest.fixture
def mock_chapter():
    """Create a mock chapter object."""
    chapter = Mock()
    chapter.id = "chapter123"
    chapter.book_id = "book123"
    chapter.title = "Chapter 1"
    chapter.content = "Chapter content"
    chapter.order = 1
    chapter.created_at = Mock()
    chapter.updated_at = Mock()
    return chapter


# ============================================================================
# Fixtures: Services
# ============================================================================

@pytest_asyncio.fixture
async def mock_user_repository():
    """Create a mock user repository."""
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_email = AsyncMock()
    repo.get_by_username = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest_asyncio.fixture
async def mock_book_repository():
    """Create a mock book repository."""
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.list_by_user = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    return repo


# ============================================================================
# Fixtures: HTTP Client
# ============================================================================

@pytest.fixture
def async_client():
    """Create an async HTTP client for testing."""
    return AsyncMock()


# ============================================================================
# Fixtures: Environment Variables
# ============================================================================

@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/test_db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("ENVIRONMENT", "test")


# ============================================================================
# Fixtures: Application
# ============================================================================

@pytest.fixture
def test_app():
    """Create FastAPI application for testing."""
    from fastapi import FastAPI
    from app.middleware.logging import LoggingMiddleware
    
    app = FastAPI(
        title="Vibe PDF Platform - Test",
        version="1.0.0"
    )
    
    # Add logging middleware
    app.add_middleware(LoggingMiddleware)
    
    return app


# ============================================================================
# Fixtures: Authentication
# ============================================================================

@pytest.fixture
def auth_headers():
    """Create authentication headers for testing."""
    return {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }


@pytest.fixture
def mock_current_user():
    """Create mock current user for authentication."""
    user = Mock()
    user.id = "user123"
    user.email = "test@example.com"
    user.username = "testuser"
    return user


# ============================================================================
# Fixtures: Test Data
# ============================================================================

@pytest.fixture
def sample_book_data():
    """Create sample book data for testing."""
    return {
        "title": "Test Book",
        "description": "A test book description",
        "topic": "Technology",
        "target_audience": "Developers"
    }


@pytest.fixture
def sample_chapter_data():
    """Create sample chapter data for testing."""
    return {
        "title": "Chapter 1: Introduction",
        "content": "This is the introduction...",
        "order": 1
    }


@pytest.fixture
def sample_user_data():
    """Create sample user data for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
        "full_name": "Test User"
    }


# ============================================================================
# Helper Functions
# ============================================================================

def create_mock_response(status_code: int, data: dict = None):
    """Create a mock HTTP response."""
    response = Mock()
    response.status_code = status_code
    response.json = Mock(return_value=data or {})
    response.text = ""
    return response


# ============================================================================
# Pytest Hooks
# ============================================================================

def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    for item in items:
        # Add markers based on test location
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        if "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)
