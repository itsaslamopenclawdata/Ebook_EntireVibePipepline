"""Database models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class UserProfileVisibility(str, enum.Enum):
    """Profile visibility settings."""
    PUBLIC = "public"
    PRIVATE = "private"
    FRIENDS = "friends"


class BookStatus(str, enum.Enum):
    """Ebook status."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Profile settings
    profile_visibility = Column(SQLEnum(UserProfileVisibility), default=UserProfileVisibility.PUBLIC)
    
    # Auth status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # OAuth fields
    google_id = Column(String(255), unique=True, nullable=True)
    
    # Relationships
    ebooks = relationship("Ebook", back_populates="author", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    reading_progress = relationship("ReadingProgress", back_populates="user", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    highlights = relationship("Highlight", back_populates="user", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    generation_tasks = relationship("GenerationTask", back_populates="user", cascade="all, delete-orphan")
    oauth_accounts = relationship("OAuthAccount", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base):
    """Refresh token model."""
    __tablename__ = "refresh_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(500), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_revoked = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")


class EmailVerification(Base):
    """Email verification token model."""
    __tablename__ = "email_verifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_used = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User")


class PasswordReset(Base):
    """Password reset token model."""
    __tablename__ = "password_resets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_used = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User")


class Ebook(Base):
    """Ebook model."""
    __tablename__ = "ebooks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    cover_image_url = Column(String(500), nullable=True)
    status = Column(SQLEnum(BookStatus), default=BookStatus.DRAFT)
    
    # Content
    content = Column(Text, nullable=True)
    genre = Column(String(100), nullable=True)
    tags = Column(JSONB, default=list)
    
    # Versioning
    version = Column(Integer, default=1)
    previous_versions = Column(JSONB, default=list)
    
    # Stats
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    rating_average = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    
    # Relationships
    author = relationship("User", back_populates="ebooks")
    chapters = relationship("Chapter", back_populates="ebook", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="ebook", cascade="all, delete-orphan")
    reading_progress = relationship("ReadingProgress", back_populates="ebook", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="ebook", cascade="all, delete-orphan")
    highlights = relationship("Highlight", back_populates="ebook", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="ebook", cascade="all, delete-orphan")


class Chapter(Base):
    """Chapter model."""
    __tablename__ = "chapters"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ebook_id = Column(UUID(as_uuid=True), ForeignKey("ebooks.id", ondelete="CASCADE"), nullable=False)
    chapter_number = Column(Integer, nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    
    # Versioning
    version = Column(Integer, default=1)
    previous_versions = Column(JSONB, default=list)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ebook = relationship("Ebook", back_populates="chapters")


class Review(Base):
    """Review model."""
    __tablename__ = "reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ebook_id = Column(UUID(as_uuid=True), ForeignKey("ebooks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    rating = Column(Integer, nullable=False)  # 1-5
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    
    # Moderation
    is_approved = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ebook = relationship("Ebook", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
    reactions = relationship("ReviewReaction", back_populates="review", cascade="all, delete-orphan")


class ReviewReaction(Base):
    """Review reaction model."""
    __tablename__ = "review_reactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(UUID(as_uuid=True), ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reaction_type = Column(String(50), nullable=False)  # "helpful", "funny", "insightful"
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    review = relationship("Review", back_populates="reactions")
    user = relationship("User")


class ReadingProgress(Base):
    """Reading progress model."""
    __tablename__ = "reading_progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ebook_id = Column(UUID(as_uuid=True), ForeignKey("ebooks.id", ondelete="CASCADE"), nullable=False)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=True)
    
    progress_percent = Column(Float, default=0.0)  # 0-100
    last_position = Column(Integer, default=0)  # Character position
    last_read_at = Column(DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="reading_progress")
    ebook = relationship("Ebook", back_populates="reading_progress")
    chapter = relationship("Chapter")


class Bookmark(Base):
    """Bookmark model."""
    __tablename__ = "bookmarks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ebook_id = Column(UUID(as_uuid=True), ForeignKey("ebooks.id", ondelete="CASCADE"), nullable=False)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=True)
    
    position = Column(Integer, nullable=False)  # Character position
    note = Column(Text, nullable=True)
    title = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="bookmarks")
    ebook = relationship("Ebook", back_populates="bookmarks")
    chapter = relationship("Chapter")


class Highlight(Base):
    """Highlight model."""
    __tablename__ = "highlights"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ebook_id = Column(UUID(as_uuid=True), ForeignKey("ebooks.id", ondelete="CASCADE"), nullable=False)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=True)
    
    start_position = Column(Integer, nullable=False)
    end_position = Column(Integer, nullable=False)
    highlighted_text = Column(Text, nullable=False)
    color = Column(String(50), default="yellow")  # yellow, green, blue, pink
    note = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="highlights")
    ebook = relationship("Ebook", back_populates="highlights")
    chapter = relationship("Chapter")


class Note(Base):
    """Note model."""
    __tablename__ = "notes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ebook_id = Column(UUID(as_uuid=True), ForeignKey("ebooks.id", ondelete="CASCADE"), nullable=False)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=True)
    
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    position = Column(Integer, nullable=True)  # Optional position in text
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notes")
    ebook = relationship("Ebook", back_populates="notes")
    chapter = relationship("Chapter")
