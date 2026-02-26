"""Database models package."""
from app.models.user import (
    User,
    RefreshToken,
    EmailVerification,
    PasswordReset,
    Ebook,
    Chapter,
    Review,
    ReviewReaction,
    ReadingProgress,
    Bookmark,
    Highlight,
    Note,
    UserProfileVisibility,
    BookStatus,
)
from app.models.generation_task import (
    GenerationTask,
    GenerationStatus,
    GenerationType,
)
from app.models.oauth import OAuthAccount
from app.models.user_session import UserSession
from app.models.book import Book, BookChapter

__all__ = [
    # User models
    "User",
    "RefreshToken",
    "EmailVerification",
    "PasswordReset",
    # Book models
    "Ebook",
    "Book",
    "Chapter",
    "BookChapter",
    "BookStatus",
    # Review models
    "Review",
    "ReviewReaction",
    # Progress models
    "ReadingProgress",
    "Bookmark",
    "Highlight",
    "Note",
    # Enums
    "UserProfileVisibility",
    # Generation models
    "GenerationTask",
    "GenerationStatus",
    "GenerationType",
    # OAuth models
    "OAuthAccount",
    # Session models
    "UserSession",
]
