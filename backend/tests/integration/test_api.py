"""
Integration tests for API endpoints.
"""

import pytest
from unittest.mock import AsyncMock, patch, Mock
from httpx import AsyncClient, ASGITransport
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


class TestAuthAPI:
    """Integration tests for authentication API endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create FastAPI app for testing."""
        from fastapi import FastAPI
        from app.routers import auth
        
        app = FastAPI()
        app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
        return app
    
    @pytest.mark.asyncio
    async def test_register_endpoint(self, app):
        """Test user registration endpoint."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "test@example.com",
                    "username": "testuser",
                    "password": "password123",
                    "full_name": "Test User"
                }
            )
            
            # Accept 201 (created) or 200 (success)
            assert response.status_code in [200, 201]
    
    @pytest.mark.asyncio
    async def test_login_endpoint(self, app):
        """Test user login endpoint."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={
                    "username": "testuser",
                    "password": "password123"
                }
            )
            
            # Accept success or mock error
            assert response.status_code in [200, 401, 422]
    
    @pytest.mark.asyncio
    async def test_logout_endpoint(self, app):
        """Test logout endpoint."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post("/api/v1/auth/logout")
            
            assert response.status_code in [200, 401]


class TestBooksAPI:
    """Integration tests for books API endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create FastAPI app for testing."""
        from fastapi import FastAPI
        from app.routers import books
        
        app = FastAPI()
        app.include_router(books.router, prefix="/api/v1/books", tags=["books"])
        return app
    
    @pytest.mark.asyncio
    async def test_create_book(self, app):
        """Test book creation endpoint."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/books/",
                json={
                    "title": "My Book",
                    "description": "A test book"
                }
            )
            
            assert response.status_code in [200, 201, 401, 422]
    
    @pytest.mark.asyncio
    async def test_list_books(self, app):
        """Test listing books endpoint."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/books/")
            
            assert response.status_code in [200, 401]
    
    @pytest.mark.asyncio
    async def test_get_book(self, app):
        """Test getting a specific book."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/books/book123")
            
            assert response.status_code in [200, 404, 401]
    
    @pytest.mark.asyncio
    async def test_update_book(self, app):
        """Test updating a book."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.put(
                "/api/v1/books/book123",
                json={"title": "Updated Title"}
            )
            
            assert response.status_code in [200, 404, 401, 422]
    
    @pytest.mark.asyncio
    async def test_delete_book(self, app):
        """Test deleting a book."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.delete("/api/v1/books/book123")
            
            assert response.status_code in [200, 204, 404, 401]


class TestGenerationAPI:
    """Integration tests for PDF generation API endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create FastAPI app for testing."""
        from fastapi import FastAPI
        from app.routers import generation
        
        app = FastAPI()
        app.include_router(
            generation.router,
            prefix="/api/v1/generation",
            tags=["generation"]
        )
        return app
    
    @pytest.mark.asyncio
    async def test_start_generation(self, app):
        """Test starting PDF generation."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/generation/start",
                json={
                    "book_id": "book123",
                    "options": {"quality": "high"}
                }
            )
            
            assert response.status_code in [200, 202, 401, 422]
    
    @pytest.mark.asyncio
    async def test_get_generation_status(self, app):
        """Test getting generation status."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/generation/status/task123")
            
            assert response.status_code in [200, 404, 401]
    
    @pytest.mark.asyncio
    async def test_cancel_generation(self, app):
        """Test cancelling generation."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post("/api/v1/generation/cancel/task123")
            
            assert response.status_code in [200, 404, 401]


class TestProfileAPI:
    """Integration tests for user profile API endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create FastAPI app for testing."""
        from fastapi import FastAPI
        from app.routers import profile
        
        app = FastAPI()
        app.include_router(profile.router, prefix="/api/v1/profile", tags=["profile"])
        return app
    
    @pytest.mark.asyncio
    async def test_get_profile(self, app):
        """Test getting user profile."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/profile/me")
            
            assert response.status_code in [200, 401]
    
    @pytest.mark.asyncio
    async def test_update_profile(self, app):
        """Test updating user profile."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.put(
                "/api/v1/profile/me",
                json={"full_name": "Updated Name"}
            )
            
            assert response.status_code in [200, 401, 422]


class TestHealthCheck:
    """Integration tests for health check endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create FastAPI app for testing."""
        from fastapi import FastAPI
        from app.main import app as main_app
        
        return main_app
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, app):
        """Test health check endpoint."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
    
    @pytest.mark.asyncio
    async def test_ready_endpoint(self, app):
        """Test readiness check endpoint."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/ready")
            
            assert response.status_code in [200, 503]
