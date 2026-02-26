"""
Unit tests for authentication module.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta


class TestAuthService:
    """Test cases for authentication service."""
    
    @pytest.fixture
    def mock_user_repository(self):
        """Create mock user repository."""
        return Mock()
    
    @pytest.fixture
    def auth_service(self, mock_user_repository):
        """Create auth service instance."""
        from app.services.auth import AuthService
        return AuthService(user_repository=mock_user_repository)
    
    @pytest.mark.asyncio
    async def test_create_access_token(self, auth_service):
        """Test JWT token creation."""
        token = auth_service.create_access_token(
            data={"sub": "testuser123"},
            expires_delta=timedelta(minutes=30)
        )
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    @pytest.mark.asyncio
    async def test_verify_password(self, auth_service):
        """Test password verification."""
        hashed = auth_service.hash_password("testpassword123")
        
        assert auth_service.verify_password("testpassword123", hashed) is True
        assert auth_service.verify_password("wrongpassword", hashed) is False
    
    @pytest.mark.asyncio
    async def test_hash_password(self, auth_service):
        """Test password hashing."""
        hashed = auth_service.hash_password("mypassword")
        
        assert hashed != "mypassword"
        assert "$" in hashed  # bcrypt format
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, auth_service, mock_user_repository):
        """Test successful user authentication."""
        mock_user = Mock()
        mock_user.username = "testuser"
        mock_user.hashed_password = auth_service.hash_password("password123")
        mock_user.is_active = True
        
        mock_user_repository.get_by_username = AsyncMock(return_value=mock_user)
        
        user = await auth_service.authenticate_user("testuser", "password123")
        
        assert user is not None
        assert user.username == "testuser"
    
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, auth_service, mock_user_repository):
        """Test authentication with wrong password."""
        mock_user = Mock()
        mock_user.username = "testuser"
        mock_user.hashed_password = auth_service.hash_password("password123")
        mock_user.is_active = True
        
        mock_user_repository.get_by_username = AsyncMock(return_value=mock_user)
        
        user = await auth_service.authenticate_user("testuser", "wrongpassword")
        
        assert user is None
    
    @pytest.mark.asyncio
    async def test_authenticate_user_inactive(self, auth_service, mock_user_repository):
        """Test authentication with inactive user."""
        mock_user = Mock()
        mock_user.username = "testuser"
        mock_user.hashed_password = auth_service.hash_password("password123")
        mock_user.is_active = False
        
        mock_user_repository.get_by_username = AsyncMock(return_value=mock_user)
        
        user = await auth_service.authenticate_user("testuser", "password123")
        
        assert user is None


class TestPasswordReset:
    """Test cases for password reset functionality."""
    
    @pytest.fixture
    def auth_service(self):
        """Create auth service instance."""
        from app.services.auth import AuthService
        return AuthService()
    
    @pytest.mark.asyncio
    async def test_create_password_reset_token(self, auth_service):
        """Test password reset token creation."""
        token = auth_service.create_password_reset_token("test@example.com")
        
        assert token is not None
        assert isinstance(token, str)
    
    @pytest.mark.asyncio
    async def test_verify_password_reset_token_valid(self, auth_service):
        """Test password reset token verification."""
        email = "test@example.com"
        token = auth_service.create_password_reset_token(email)
        
        result = auth_service.verify_password_reset_token(token)
        
        assert result == email
    
    @pytest.mark.asyncio
    async def test_verify_password_reset_token_invalid(self, auth_service):
        """Test password reset token verification with invalid token."""
        result = auth_service.verify_password_reset_token("invalid.token.here")
        
        assert result is None


class TestOAuth:
    """Test cases for OAuth authentication."""
    
    @pytest.fixture
    def auth_service(self):
        """Create auth service instance."""
        from app.services.auth import AuthService
        return AuthService()
    
    def test_google_oauth_url(self, auth_service):
        """Test Google OAuth URL generation."""
        url = auth_service.get_google_oauth_url()
        
        assert "accounts.google.com" in url
        assert "client_id" in url
    
    @pytest.mark.asyncio
    async def test_google_callback_invalid_state(self, auth_service):
        """Test Google OAuth callback with invalid state."""
        with pytest.raises(ValueError, match="Invalid state"):
            await auth_service.handle_google_callback("invalid_code", "wrong_state", "original_state")


class TestSessionManagement:
    """Test cases for session management."""
    
    @pytest.fixture
    def auth_service(self):
        """Create auth service instance."""
        from app.services.auth import AuthService
        return AuthService()
    
    @pytest.mark.asyncio
    async def test_create_session(self, auth_service):
        """Test session creation."""
        session = await auth_service.create_session(
            user_id="user123",
            device_info={"browser": "Chrome"},
            ip_address="192.168.1.1"
        )
        
        assert session is not None
        assert session.user_id == "user123"
        assert session.token is not None
    
    @pytest.mark.asyncio
    async def test_validate_session_valid(self, auth_service):
        """Test session validation with valid token."""
        session = await auth_service.create_session(
            user_id="user123",
            device_info={},
            ip_address="192.168.1.1"
        )
        
        valid = await auth_service.validate_session(session.token)
        
        assert valid is True
    
    @pytest.mark.asyncio
    async def test_validate_session_invalid(self, auth_service):
        """Test session validation with invalid token."""
        valid = await auth_service.validate_session("invalid.session.token")
        
        assert valid is False
