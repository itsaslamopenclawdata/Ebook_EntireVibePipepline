"""Profile service for user profile management."""
import uuid
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.user import User, UserProfileVisibility, Ebook, Review, ReadingProgress
from app.models.oauth import OAuthAccount
from app.models.user_session import UserSession

logger = logging.getLogger(__name__)


class ProfileService:
    """Service for managing user profiles."""
    
    def __init__(self, db: AsyncSession):
        """Initialize profile service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def get_profile(
        self,
        user_id: uuid.UUID,
    ) -> Optional[User]:
        """Get user profile.
        
        Args:
            user_id: ID of the user
            
        Returns:
            User instance or None
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_profile_by_username(
        self,
        username: str,
    ) -> Optional[User]:
        """Get user profile by username.
        
        Args:
            username: Username to look up
            
        Returns:
            User instance or None
        """
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def update_profile(
        self,
        user_id: uuid.UUID,
        **kwargs,
    ) -> Optional[User]:
        """Update user profile.
        
        Args:
            user_id: ID of the user
            **kwargs: Fields to update (full_name, bio, avatar_url, etc.)
            
        Returns:
            Updated User or None
        """
        user = await self.get_profile(user_id)
        if not user:
            return None
        
        # Fields that users can update themselves
        allowed_fields = {
            "full_name",
            "bio",
            "avatar_url",
            "profile_visibility",
        }
        
        for key, value in kwargs.items():
            if key in allowed_fields and hasattr(user, key):
                setattr(user, key, value)
        
        user.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(user)
        
        logger.info(f"Updated profile for user: {user_id}")
        return user
    
    async def get_public_profile_data(
        self,
        user_id: uuid.UUID,
    ) -> Optional[Dict[str, Any]]:
        """Get public profile data for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dict with public profile data or None
        """
        user = await self.get_profile(user_id)
        if not user:
            return None
        
        # Check visibility
        if user.profile_visibility == UserProfileVisibility.PRIVATE:
            return {
                "username": user.username,
                "is_private": True,
            }
        
        # Get ebook count
        ebook_count = await self._count_user_ebooks(user_id)
        
        # Get review count
        review_count = await self._count_user_reviews(user_id)
        
        return {
            "id": str(user.id),
            "username": user.username,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "bio": user.bio,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "ebook_count": ebook_count,
            "review_count": review_count,
            "profile_visibility": user.profile_visibility.value,
        }
    
    async def _count_user_ebooks(
        self,
        user_id: uuid.UUID,
    ) -> int:
        """Count published ebooks for a user."""
        result = await self.db.execute(
            select(func.count(Ebook.id))
            .where(
                Ebook.author_id == user_id,
                Ebook.status == "published",
            )
        )
        return result.scalar() or 0
    
    async def _count_user_reviews(
        self,
        user_id: uuid.UUID,
    ) -> int:
        """Count reviews by a user."""
        result = await self.db.execute(
            select(func.count(Review.id))
            .where(Review.user_id == user_id)
        )
        return result.scalar() or 0
    
    # ========== OAuth Management ==========
    
    async def link_oauth_account(
        self,
        user_id: uuid.UUID,
        provider: str,
        provider_account_id: str,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        scope: Optional[List[str]] = None,
    ) -> OAuthAccount:
        """Link an OAuth account to a user.
        
        Args:
            user_id: ID of the user
            provider: OAuth provider (google, github, etc.)
            provider_account_id: ID from the OAuth provider
            access_token: OAuth access token
            refresh_token: OAuth refresh token
            expires_at: Token expiration time
            scope: OAuth scope
            
        Returns:
            Created OAuthAccount instance
        """
        # Check if already linked
        existing = await self.db.execute(
            select(OAuthAccount).where(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_account_id == provider_account_id,
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"OAuth account already linked")
        
        oauth_account = OAuthAccount(
            user_id=user_id,
            provider=provider,
            provider_account_id=provider_account_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            scope=scope or [],
        )
        
        self.db.add(oauth_account)
        await self.db.commit()
        await self.db.refresh(oauth_account)
        
        logger.info(f"Linked {provider} account to user {user_id}")
        return oauth_account
    
    async def unlink_oauth_account(
        self,
        user_id: uuid.UUID,
        provider: str,
    ) -> bool:
        """Unlink an OAuth account from a user.
        
        Args:
            user_id: ID of the user
            provider: OAuth provider to unlink
            
        Returns:
            True if unlinked
        """
        result = await self.db.execute(
            select(OAuthAccount).where(
                OAuthAccount.user_id == user_id,
                OAuthAccount.provider == provider,
            )
        )
        oauth_account = result.scalar_one_or_none()
        
        if not oauth_account:
            return False
        
        await self.db.delete(oauth_account)
        await self.db.commit()
        
        logger.info(f"Unlinked {provider} account from user {user_id}")
        return True
    
    async def get_linked_accounts(
        self,
        user_id: uuid.UUID,
    ) -> List[Dict[str, Any]]:
        """Get OAuth accounts linked to a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of linked account info (without tokens)
        """
        result = await self.db.execute(
            select(OAuthAccount).where(OAuthAccount.user_id == user_id)
        )
        
        accounts = []
        for account in result.scalars().all():
            accounts.append({
                "id": str(account.id),
                "provider": account.provider,
                "provider_account_id": account.provider_account_id,
                "created_at": account.created_at.isoformat() if account.created_at else None,
                "expires_at": account.expires_at.isoformat() if account.expires_at else None,
            })
        
        return accounts
    
    # ========== Session Management ==========
    
    async def create_session(
        self,
        user_id: uuid.UUID,
        session_token: str,
        device_info: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        expires_at: datetime = None,
    ) -> UserSession:
        """Create a new user session.
        
        Args:
            user_id: ID of the user
            session_token: Unique session token
            device_info: Device information
            ip_address: IP address
            user_agent: User agent string
            expires_at: Session expiration time
            
        Returns:
            Created UserSession instance
        """
        session = UserSession(
            user_id=user_id,
            session_token=session_token,
            device_info=device_info or {},
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at or datetime.utcnow(),
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        logger.info(f"Created session for user {user_id}")
        return session
    
    async def get_active_sessions(
        self,
        user_id: uuid.UUID,
    ) -> List[UserSession]:
        """Get active sessions for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of active UserSession instances
        """
        result = await self.db.execute(
            select(UserSession)
            .where(
                UserSession.user_id == user_id,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow(),
            )
            .order_by(UserSession.last_active_at.desc())
        )
        return list(result.scalars().all())
    
    async def terminate_session(
        self,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
    ) -> bool:
        """Terminate a user session.
        
        Args:
            user_id: ID of the user
            session_id: ID of the session
            
        Returns:
            True if terminated
        """
        result = await self.db.execute(
            select(UserSession).where(
                UserSession.id == session_id,
                UserSession.user_id == user_id,
            )
        )
        session = result.scalar_one_or_none()
        
        if not session:
            return False
        
        session.is_active = False
        await self.db.commit()
        
        logger.info(f"Terminated session {session_id} for user {user_id}")
        return True
    
    async def terminate_all_sessions(
        self,
        user_id: uuid.UUID,
        except_current: bool = True,
    ) -> int:
        """Terminate all user sessions.
        
        Args:
            user_id: ID of the user
            except_current: Whether to keep current session
            
        Returns:
            Number of sessions terminated
        """
        query = update(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.is_active == True,
        )
        
        result = await self.db.execute(query)
        await self.db.commit()
        
        count = result.rowcount
        logger.info(f"Terminated {count} sessions for user {user_id}")
        return count
    
    # ========== Reading Stats ==========
    
    async def get_reading_stats(
        self,
        user_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """Get reading statistics for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dict with reading stats
        """
        # Get reading progress count
        result = await self.db.execute(
            select(func.count(ReadingProgress.id))
            .where(ReadingProgress.user_id == user_id)
        )
        books_in_progress = result.scalar() or 0
        
        # Get completed books
        result = await self.db.execute(
            select(func.count(ReadingProgress.id))
            .where(
                ReadingProgress.user_id == user_id,
                ReadingProgress.progress_percent >= 100,
            )
        )
        books_completed = result.scalar() or 0
        
        return {
            "books_in_progress": books_in_progress,
            "books_completed": books_completed,
        }


async def get_profile_service(db: AsyncSession) -> ProfileService:
    """Get profile service instance.
    
    Args:
        db: Database session
        
    Returns:
        ProfileService instance
    """
    return ProfileService(db)
