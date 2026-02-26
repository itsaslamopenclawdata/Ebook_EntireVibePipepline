"""
Unit tests for user profile module.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime


class TestUserProfileService:
    """Test cases for user profile service."""
    
    @pytest.fixture
    def mock_user_repository(self):
        """Create mock user repository."""
        return Mock()
    
    @pytest.fixture
    def profile_service(self, mock_user_repository):
        """Create profile service instance."""
        from app.services.profile import UserProfileService
        return UserProfileService(user_repository=mock_user_repository)
    
    @pytest.mark.asyncio
    async def test_get_profile(self, profile_service, mock_user_repository):
        """Test getting user profile."""
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.email = "test@example.com"
        mock_user.full_name = "Test User"
        mock_user.avatar_url = None
        mock_user.bio = None
        mock_user.created_at = datetime.now()
        
        mock_user_repository.get_by_id = AsyncMock(return_value=mock_user)
        
        profile = await profile_service.get_profile("user123")
        
        assert profile is not None
        assert profile.id == "user123"
        assert profile.email == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_update_profile(self, profile_service, mock_user_repository):
        """Test updating user profile."""
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.full_name = "Updated Name"
        
        mock_user_repository.update = AsyncMock(return_value=mock_user)
        
        profile = await profile_service.update_profile(
            "user123",
            full_name="Updated Name"
        )
        
        assert profile.full_name == "Updated Name"
        mock_user_repository.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_avatar(self, profile_service, mock_user_repository):
        """Test updating user avatar."""
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.avatar_url = "https://example.com/new-avatar.jpg"
        
        mock_user_repository.update = AsyncMock(return_value=mock_user)
        
        profile = await profile_service.update_avatar(
            "user123",
            "https://example.com/new-avatar.jpg"
        )
        
        assert profile.avatar_url == "https://example.com/new-avatar.jpg"
    
    @pytest.mark.asyncio
    async def test_get_user_settings(self, profile_service, mock_user_repository):
        """Test getting user settings."""
        mock_settings = {
            "email_notifications": True,
            "push_notifications": False,
            "theme": "dark",
            "language": "en"
        }
        
        mock_user = Mock()
        mock_user.settings = mock_settings
        
        mock_user_repository.get_by_id = AsyncMock(return_value=mock_user)
        
        settings = await profile_service.get_settings("user123")
        
        assert settings == mock_settings
    
    @pytest.mark.asyncio
    async def test_update_settings(self, profile_service, mock_user_repository):
        """Test updating user settings."""
        mock_user = Mock()
        mock_user.settings = {"theme": "light"}
        
        mock_user_repository.update = AsyncMock(return_value=mock_user)
        
        settings = await profile_service.update_settings(
            "user123",
            theme="dark"
        )
        
        mock_user_repository.update.assert_called_once()


class TestUserPreferences:
    """Test cases for user preferences."""
    
    @pytest.fixture
    def preferences_service(self):
        """Create preferences service instance."""
        from app.services.profile import UserPreferencesService
        return UserPreferencesService()
    
    @pytest.mark.asyncio
    async def test_set_preference(self, preferences_service):
        """Test setting user preference."""
        result = await preferences_service.set(
            user_id="user123",
            key="pdf_quality",
            value="high"
        )
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_get_preference(self, preferences_service):
        """Test getting user preference."""
        await preferences_service.set(
            user_id="user123",
            key="pdf_quality",
            value="high"
        )
        
        value = await preferences_service.get("user123", "pdf_quality")
        
        assert value == "high"
    
    @pytest.mark.asyncio
    async def test_get_preference_default(self, preferences_service):
        """Test getting preference with default value."""
        value = await preferences_service.get(
            user_id="user123",
            key="nonexistent",
            default="default_value"
        )
        
        assert value == "default_value"
    
    @pytest.mark.asyncio
    async def test_delete_preference(self, preferences_service):
        """Test deleting user preference."""
        await preferences_service.set(
            user_id="user123",
            key="temp_preference",
            value="temp"
        )
        
        result = await preferences_service.delete("user123", "temp_preference")
        
        assert result is True


class TestUserActivity:
    """Test cases for user activity tracking."""
    
    @pytest.fixture
    def activity_service(self):
        """Create activity service instance."""
        from app.services.profile import UserActivityService
        return UserActivityService()
    
    @pytest.mark.asyncio
    async def test_log_activity(self, activity_service):
        """Test logging user activity."""
        result = await activity_service.log(
            user_id="user123",
            action="book_created",
            metadata={"book_id": "book123"}
        )
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_get_recent_activity(self, activity_service):
        """Test getting recent activity."""
        activities = await activity_service.get_recent(
            user_id="user123",
            limit=10
        )
        
        assert isinstance(activities, list)
    
    @pytest.mark.asyncio
    async def test_get_activity_stats(self, activity_service):
        """Test getting activity statistics."""
        stats = await activity_service.get_stats("user123")
        
        assert stats is not None
        assert "total_books" in stats
        assert "total_generations" in stats


class TestUserProfileValidation:
    """Test cases for profile validation."""
    
    def test_validate_email(self):
        """Test email validation."""
        from app.schemas.profile import ProfileUpdate
        
        # Valid email
        profile = ProfileUpdate(email="valid@example.com")
        assert profile.email == "valid@example.com"
        
        # Invalid email
        with pytest.raises(Exception):
            ProfileUpdate(email="invalid-email")
    
    def test_validate_full_name(self):
        """Test full name validation."""
        from app.schemas.profile import ProfileUpdate
        
        # Valid name
        profile = ProfileUpdate(full_name="John Doe")
        assert profile.full_name == "John Doe"
        
        # Too long name
        with pytest.raises(Exception):
            ProfileUpdate(full_name="x" * 200)
