"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum


# Enums
class UserProfileVisibilityEnum(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    FRIENDS = "friends"


class BookStatusEnum(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


# User Schemas
class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8)
    username: Optional[str] = Field(None, min_length=3, max_length=100)


class UserUpdate(BaseModel):
    """Schema for user update."""
    full_name: Optional[str] = None
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    profile_visibility: Optional[UserProfileVisibilityEnum] = None


class UserResponse(BaseModel):
    """Schema for user response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    email: str
    username: Optional[str]
    full_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    profile_visibility: UserProfileVisibilityEnum
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    last_login: Optional[datetime]


class UserPublicResponse(BaseModel):
    """Public profile response (limited fields)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    username: Optional[str]
    full_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    profile_visibility: UserProfileVisibilityEnum
    created_at: datetime


# Auth Schemas
class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    new_password: str = Field(..., min_length=8)


class EmailVerificationRequest(BaseModel):
    """Schema for email verification request."""
    email: EmailStr


class EmailVerificationConfirm(BaseModel):
    """Schema for email verification confirmation."""
    token: str


# Ebook Schemas
class ChapterBase(BaseModel):
    """Base chapter schema."""
    title: str
    content: Optional[str] = None


class ChapterCreate(ChapterBase):
    """Schema for chapter creation."""
    chapter_number: int


class ChapterUpdate(BaseModel):
    """Schema for chapter update."""
    title: Optional[str] = None
    content: Optional[str] = None


class ChapterResponse(BaseModel):
    """Schema for chapter response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    ebook_id: UUID
    chapter_number: int
    title: str
    content: Optional[str]
    version: int
    created_at: datetime
    updated_at: datetime


class EbookBase(BaseModel):
    """Base ebook schema."""
    title: str
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    genre: Optional[str] = None
    tags: List[str] = []


class EbookCreate(EbookBase):
    """Schema for ebook creation."""
    content: Optional[str] = None


class EbookUpdate(BaseModel):
    """Schema for ebook update."""
    title: Optional[str] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    content: Optional[str] = None
    genre: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[BookStatusEnum] = None


class EbookResponse(BaseModel):
    """Schema for ebook response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    author_id: UUID
    title: str
    description: Optional[str]
    cover_image_url: Optional[str]
    status: BookStatusEnum
    content: Optional[str]
    genre: Optional[str]
    tags: List[str]
    version: int
    view_count: int
    download_count: int
    rating_average: float
    rating_count: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    author: Optional[UserPublicResponse] = None


class EbookListResponse(BaseModel):
    """Schema for ebook list response."""
    items: List[EbookResponse]
    total: int
    skip: int
    limit: int


# Progress Schemas
class ReadingProgressBase(BaseModel):
    """Base reading progress schema."""
    progress_percent: float = Field(..., ge=0, le=100)
    last_position: int = 0
    chapter_id: Optional[UUID] = None


class ReadingProgressCreate(ReadingProgressBase):
    """Schema for reading progress creation."""
    ebook_id: UUID


class ReadingProgressUpdate(BaseModel):
    """Schema for reading progress update."""
    progress_percent: Optional[float] = Field(None, ge=0, le=100)
    last_position: Optional[int] = None
    chapter_id: Optional[UUID] = None


class ReadingProgressResponse(BaseModel):
    """Schema for reading progress response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    ebook_id: UUID
    chapter_id: Optional[UUID]
    progress_percent: float
    last_position: int
    last_read_at: datetime
    created_at: datetime
    updated_at: datetime


# Bookmark Schemas
class BookmarkBase(BaseModel):
    """Base bookmark schema."""
    position: int
    note: Optional[str] = None
    title: Optional[str] = None
    chapter_id: Optional[UUID] = None


class BookmarkCreate(BookmarkBase):
    """Schema for bookmark creation."""
    ebook_id: UUID


class BookmarkUpdate(BaseModel):
    """Schema for bookmark update."""
    note: Optional[str] = None
    title: Optional[str] = None


class BookmarkResponse(BaseModel):
    """Schema for bookmark response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    ebook_id: UUID
    chapter_id: Optional[UUID]
    position: int
    note: Optional[str]
    title: Optional[str]
    created_at: datetime
    updated_at: datetime


# Highlight Schemas
class HighlightBase(BaseModel):
    """Base highlight schema."""
    start_position: int
    end_position: int
    highlighted_text: str
    color: str = "yellow"
    note: Optional[str] = None
    chapter_id: Optional[UUID] = None


class HighlightCreate(HighlightBase):
    """Schema for highlight creation."""
    ebook_id: UUID


class HighlightUpdate(BaseModel):
    """Schema for highlight update."""
    color: Optional[str] = None
    note: Optional[str] = None


class HighlightResponse(BaseModel):
    """Schema for highlight response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    ebook_id: UUID
    chapter_id: Optional[UUID]
    start_position: int
    end_position: int
    highlighted_text: str
    color: str
    note: Optional[str]
    created_at: datetime
    updated_at: datetime


# Note Schemas
class NoteBase(BaseModel):
    """Base note schema."""
    title: Optional[str] = None
    content: str
    position: Optional[int] = None
    chapter_id: Optional[UUID] = None


class NoteCreate(NoteBase):
    """Schema for note creation."""
    ebook_id: UUID


class NoteUpdate(BaseModel):
    """Schema for note update."""
    title: Optional[str] = None
    content: Optional[str] = None
    position: Optional[int] = None


class NoteResponse(BaseModel):
    """Schema for note response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    ebook_id: UUID
    chapter_id: Optional[UUID]
    title: Optional[str]
    content: str
    position: Optional[int]
    created_at: datetime
    updated_at: datetime


# Review Schemas
class ReviewBase(BaseModel):
    """Base review schema."""
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = None
    content: Optional[str] = None


class ReviewCreate(ReviewBase):
    """Schema for review creation."""
    ebook_id: UUID


class ReviewUpdate(BaseModel):
    """Schema for review update."""
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = None
    content: Optional[str] = None


class ReviewResponse(BaseModel):
    """Schema for review response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    ebook_id: UUID
    user_id: UUID
    rating: int
    title: Optional[str]
    content: Optional[str]
    is_approved: bool
    is_featured: bool
    created_at: datetime
    updated_at: datetime
    user: Optional[UserPublicResponse] = None
    helpful_count: int = 0
    funny_count: int = 0
    insightful_count: int = 0


class ReviewListResponse(BaseModel):
    """Schema for review list response."""
    items: List[ReviewResponse]
    total: int
    skip: int
    limit: int


# Review Reaction Schemas
class ReviewReactionCreate(BaseModel):
    """Schema for review reaction creation."""
    reaction_type: str = Field(..., pattern="^(helpful|funny|insightful)$")


class ReviewReactionResponse(BaseModel):
    """Schema for review reaction response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    review_id: UUID
    user_id: UUID
    reaction_type: str
    created_at: datetime


# Generation Schemas
class GenerationStatusEnum(str, Enum):
    """Generation status enum."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GenerationRequest(BaseModel):
    """Schema for book generation request."""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    genre: Optional[str] = None
    target_word_count: int = Field(default=50000, ge=1000, le=200000)
    style: Optional[str] = None
    chapter_count: Optional[int] = Field(None, ge=1, le=100)
    prompt: Optional[str] = None


class GenerationProgressResponse(BaseModel):
    """Schema for generation progress response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    book_id: UUID
    status: GenerationStatusEnum
    progress_percent: float
    current_chapter: Optional[int]
    total_chapters: Optional[int]
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime


class GenerationStartResponse(BaseModel):
    """Schema for generation start response."""
    generation_id: UUID
    book_id: UUID
    status: GenerationStatusEnum
    message: str


class GenerationCancelResponse(BaseModel):
    """Schema for generation cancel response."""
    message: str
    status: GenerationStatusEnum


class GenerationRetryResponse(BaseModel):
    """Schema for generation retry response."""
    generation_id: UUID
    book_id: UUID
    status: GenerationStatusEnum
    message: str


# Book (User's Library) Schemas
class BookBase(BaseModel):
    """Base book schema."""
    title: str
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    genre: Optional[str] = None
    tags: List[str] = []


class BookCreate(BookBase):
    """Schema for book creation."""
    content: Optional[str] = None


class BookUpdate(BaseModel):
    """Schema for book update."""
    title: Optional[str] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    content: Optional[str] = None
    genre: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[BookStatusEnum] = None


class BookResponse(BaseModel):
    """Schema for book response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    author_id: UUID
    title: str
    description: Optional[str]
    cover_image_url: Optional[str]
    status: BookStatusEnum
    content: Optional[str]
    genre: Optional[str]
    tags: List[str]
    version: int
    view_count: int
    download_count: int
    rating_average: float
    rating_count: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    author: Optional[UserPublicResponse] = None


class BookListResponse(BaseModel):
    """Schema for book list response."""
    items: List[BookResponse]
    total: int
    skip: int
    limit: int


class ChapterInBookResponse(BaseModel):
    """Schema for chapter in book response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    ebook_id: UUID
    chapter_number: int
    title: str
    content: Optional[str]
    version: int
    created_at: datetime
    updated_at: datetime


class ChapterListResponse(BaseModel):
    """Schema for chapter list response."""
    items: List[ChapterInBookResponse]
    total: int


class ChapterCreateInBook(BaseModel):
    """Schema for chapter creation within a book."""
    title: str
    content: Optional[str] = None
    chapter_number: int


# Profile Schemas
class ProfileResponse(BaseModel):
    """Schema for profile response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    email: str
    username: Optional[str]
    full_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    profile_visibility: UserProfileVisibilityEnum
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    last_login: Optional[datetime]


class ProfileUpdate(BaseModel):
    """Schema for profile update."""
    full_name: Optional[str] = None
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    profile_visibility: Optional[UserProfileVisibilityEnum] = None


class ReadingPreferences(BaseModel):
    """Schema for reading preferences."""
    preferred_genres: List[str] = []
    font_size: Optional[str] = None
    theme: Optional[str] = None  # light, dark, sepia
    reading_speed_wpm: Optional[int] = Field(None, ge=50, le=1000)
    auto_scroll: bool = False


class ReadingPreferencesUpdate(BaseModel):
    """Schema for updating reading preferences."""
    preferred_genres: Optional[List[str]] = None
    font_size: Optional[str] = None
    theme: Optional[str] = None
    reading_speed_wpm: Optional[int] = Field(None, ge=50, le=1000)
    auto_scroll: Optional[bool] = None


class ActivityItem(BaseModel):
    """Schema for activity item."""
    id: UUID
    activity_type: str
    book_id: Optional[UUID]
    book_title: Optional[str]
    chapter_id: Optional[UUID]
    chapter_title: Optional[str]
    description: str
    created_at: datetime


class ActivityListResponse(BaseModel):
    """Schema for activity list response."""
    items: List[ActivityItem]
    total: int
    skip: int
    limit: int


# MCP Integration Schemas
class GoogleDriveUploadRequest(BaseModel):
    """Schema for Google Drive upload request."""
    file_name: str
    folder_id: Optional[str] = None
    mime_type: Optional[str] = "application/pdf"


class GoogleDriveUploadResponse(BaseModel):
    """Schema for Google Drive upload response."""
    file_id: str
    file_name: str
    web_view_link: str
    download_link: str
    created_time: datetime


class GoogleDriveDownloadRequest(BaseModel):
    """Schema for Google Drive download request."""
    file_id: str
    output_file_name: Optional[str] = None


class GoogleDriveDownloadResponse(BaseModel):
    """Schema for Google Drive download response."""
    file_name: str
    file_path: str
    mime_type: str
    size_bytes: int


class GoogleDriveFileResponse(BaseModel):
    """Schema for Google Drive file info."""
    file_id: str
    file_name: str
    mime_type: str
    size_bytes: int
    web_view_link: str
    created_time: datetime
    modified_time: datetime


class PDFManipulationRequest(BaseModel):
    """Schema for PDF manipulation request."""
    operation: str = Field(..., pattern="^(merge|split|extract|compress|watermark)$")


class PDFMergeRequest(PDFManipulationRequest):
    """Schema for PDF merge request."""
    operation: str = "merge"
    file_ids: List[str] = Field(..., min_items=2)
    output_name: Optional[str] = None


class PDFSplitRequest(PDFManipulationRequest):
    """Schema for PDF split request."""
    operation: str = "split"
    file_id: str
    split_type: str = Field(..., pattern="^(pages|range)$")
    pages: Optional[List[int]] = None  # For split by pages
    start_page: Optional[int] = None  # For split by range
    end_page: Optional[int] = None


class PDFExtractRequest(PDFManipulationRequest):
    """Schema for PDF extract request."""
    operation: str = "extract"
    file_id: str
    pages: List[int] = Field(..., min_items=1)
    output_name: Optional[str] = None


class PDFCompressRequest(PDFManipulationRequest):
    """Schema for PDF compress request."""
    operation: str = "compress"
    file_id: str
    quality: str = Field(default="medium", pattern="^(low|medium|high)$")


class PDFWatermarkRequest(PDFManipulationRequest):
    """Schema for PDF watermark request."""
    operation: str = "watermark"
    file_id: str
    text: str
    position: str = Field(default="center", pattern="^(center|corner|custom)$")
    opacity: float = Field(default=0.3, ge=0.1, le=1.0)
    font_size: Optional[int] = Field(default=48, ge=8, le=144)


class PDFManipulationResponse(BaseModel):
    """Schema for PDF manipulation response."""
    operation: str
    success: bool
    output_file_id: Optional[str] = None
    output_file_name: Optional[str] = None
    output_file_path: Optional[str] = None
    message: str


class PDFListResponse(BaseModel):
    """Schema for PDF list response."""
    items: List[GoogleDriveFileResponse]
    total: int


# Common Response Schemas
class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


class ErrorResponse(BaseModel):
    """Error response."""
    detail: str
