"""OAuth account models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class OAuthAccount(Base):
    """OAuth account model for storing third-party OAuth credentials."""
    __tablename__ = "oauth_accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # OAuth provider
    provider = Column(String(50), nullable=False)  # "google", "github", "facebook", etc.
    provider_account_id = Column(String(255), nullable=False)  # ID from the OAuth provider
    
    # OAuth tokens (encrypted in production)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    token_type = Column(String(50), default="Bearer")
    
    # Additional provider data
    provider_data = Column(JSONB, default=dict)
    
    # Scope granted by user
    scope = Column(JSONB, default=list)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="oauth_accounts")
    
    # Unique constraint on provider + provider_account_id
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )
