# Pydantic Schemas - Quick Reference Guide
## Vibe PDF Platform Backend

**Location:** `Backend/app/schemas/`

---

## Quick Index

| Domain | File | Schemas | Purpose |
|--------|------|---------|---------|
| **User** | `user.py` | 6 | Authentication & user management |
| **Book** | `book.py` | 5 | Book creation & updates |
| **Chapter** | `chapter.py` | 6 | Chapter hierarchy & content |
| **Generation** | `generation.py` | 5 | Background task management |

---

## Import Examples

```python
# Import from schemas package
from app.schemas import (
    UserCreate, UserResponse, UserLogin,
    BookCreate, BookResponse, BookUpdate,
    ChapterCreate, ChapterResponse,
    GenerationStartRequest, GenerationStatusResponse
)

# Import enums
from app.models.book import BookStatus, InputMethod
from app.models.generation import TaskStatus

# Import specific schemas
from app.schemas.user import TokenResponse
from app.schemas.chapter import ChapterOutline, ChapterOutlineItem
```

---

## User Schemas

### UserBase
**Base fields for user data**
```python
class UserBase(BaseModel):
    email: EmailStr              # Validated email format
    name: str                    # 1-255 characters
```

### UserCreate
**User registration**
```python
class UserCreate(UserBase):
    password: str                # 8-100 characters
```

**Usage:**
```python
user = UserCreate(
    email="user@example.com",
    name="John Doe",
    password="SecurePass123!"
)
```

### UserLogin
**Login credentials**
```python
class UserLogin(BaseModel):
    email: EmailStr
    password: str
```

### UserResponse
**User data in API responses**
```python
class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    name: str
    avatar_url: str | None       # Nullable
    is_active: bool              # Default: True
    created_at: datetime
```

### TokenResponse
**JWT authentication tokens**
```python
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str              # Default: "bearer"
```

### GoogleAuthRequest
**Google OAuth authentication**
```python
class GoogleAuthRequest(BaseModel):
    id_token: str                # Google ID token
```

---

## Book Schemas

### BookBase
**Base book fields**
```python
class BookBase(BaseModel):
    title: str                   # 1-500 characters
    topic: str | None            # 0-1000 characters, nullable
```

### BookCreate
**Create new book**
```python
class BookCreate(BookBase):
    input_method: InputMethod    # Enum: TOPIC_DESCRIPTION, STRUCTURED_OUTLINE, EXISTING_DOCUMENT
    input_data: dict[str, Any]   # Method-specific data
```

**Usage:**
```python
from app.models.book import InputMethod

book = BookCreate(
    title="Introduction to AI",
    topic="AI fundamentals",
    input_method=InputMethod.TOPIC_DESCRIPTION,
    input_data={
        "topic": "Artificial Intelligence",
        "chapters": 10,
        "style": "academic"
    }
)
```

### BookUpdate
**Partial book updates**
```python
class BookUpdate(BaseModel):
    title: str | None
    topic: str | None
    # All fields optional for partial updates
```

### BookResponse
**Full book data**
```python
class BookResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    topic: str | None
    status: BookStatus            # Enum: DRAFT, OUTLINING, GENERATING_CONTENT, etc.
    input_method: InputMethod
    page_count: int | None
    drive_url: str | None
    cover_url: str | None
    progress_percentage: int     # 0-100 range
    current_step: str | None
    error_message: str | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
```

### BookStatusResponse
**Lightweight status updates**
```python
class BookStatusResponse(BaseModel):
    status: BookStatus
    progress_percentage: int     # 0-100 range
    current_step: str | None
```

---

## Chapter Schemas

### ChapterOutlineItem
**Hierarchical outline item**
```python
class ChapterOutlineItem(BaseModel):
    title: str                   # 1-500 characters, auto-stripped
    level: int                   # 1-3 range
    chapter_number: int          # >= 1
    description: str | None      # 0-2000 characters
    estimated_pages: int | None  # 1-100 range
    children: list[ChapterOutlineItem]  # Recursive structure
```

**Usage:**
```python
outline = ChapterOutlineItem(
    title="Neural Networks",
    level=1,
    chapter_number=1,
    children=[
        ChapterOutlineItem(
            title="Perceptrons",
            level=2,              # Must be > parent level
            chapter_number=1,
            description="Basic building block"
        )
    ]
)
```

**Validation:** Children must have `level > parent.level`

### ChapterOutline
**Outline generation request**
```python
class ChapterOutline(BaseModel):
    topic: str                   # 1-500 characters, auto-normalized
    target_chapters: int         # 1-50 range
    max_depth: int               # 1-3 range, default: 2
    tone: str | None             # Default: "educational"
    target_audience: str | None  # Default: "general"
    existing_outline: list[ChapterOutlineItem] | None
    outline_notes: str | None    # 0-5000 characters
```

**Usage:**
```python
outline = ChapterOutline(
    topic="Artificial Intelligence",
    target_chapters=10,
    max_depth=2,
    tone="academic",
    target_audience="beginner"
)
```

### ChapterCreate
**Create chapter**
```python
class ChapterCreate(BaseModel):
    title: str                   # 1-500 characters, auto-stripped
    content: str | None          # Line endings normalized
    chapter_number: int          # >= 1
    parent_chapter_id: UUID | None
    level: int                   # 1-3 range, default: 1
    estimated_pages: int | None  # 1-100 range
```

**Usage:**
```python
chapter = ChapterCreate(
    title="Introduction to Neural Networks",
    content="# Introduction\n\nNeural networks are...",
    chapter_number=1,
    level=1,
    estimated_pages=15
)
```

### ChapterResponse
**Chapter data**
```python
class ChapterResponse(BaseModel):
    id: UUID
    book_id: UUID
    chapter_number: int
    title: str
    content: str | None
    content_summary: str | None
    parent_chapter_id: UUID | None
    level: int                   # 1-3 range
    infographic_url: str | None
    page_start: int | None       # >= 1
    page_end: int | None         # >= 1
    page_count: int | None       # Computed from start/end
    is_top_level: bool           # Computed: True if no parent
    created_at: datetime
    updated_at: datetime
```

### ChapterUpdate
**Partial chapter updates**
```python
class ChapterUpdate(BaseModel):
    title: str | None
    content: str | None
    chapter_number: int | None
    parent_chapter_id: UUID | None
    level: int | None            # 1-3 range
    infographic_url: str | None
```

### ChapterListResponse
**Paginated chapter list**
```python
class ChapterListResponse(BaseModel):
    items: list[ChapterResponse]
    total: int                   # Total matching chapters
    page: int                    # Current page (>= 1)
    page_size: int               # 1-100 range
    total_pages: int             # Total pages
```

---

## Generation Schemas

### GenerationStartRequest
**Start generation task**
```python
class GenerationStartRequest(BaseModel):
    book_id: UUID
    options: dict[str, Any]      # Default: {}
```

**Usage:**
```python
request = GenerationStartRequest(
    book_id=uuid4(),
    options={
        "include_infographics": True,
        "style": "academic"
    }
)
```

### GenerationStatusResponse
**Task progress status**
```python
class GenerationStatusResponse(BaseModel):
    task_id: UUID
    status: TaskStatus           # Enum: PENDING, STARTED, PROGRESS, SUCCESS, FAILURE, REVOKED, RETRY
    progress: int                # 0-100 range, default: 0
    current_step: str | None
    result: dict[str, Any] | None
    error: str | None
```

### GenerationResultResponse
**Completed task results**
```python
class GenerationResultResponse(BaseModel):
    task_id: UUID
    status: TaskStatus           # Should be SUCCESS
    download_url: str | None
    drive_url: str | None
    page_count: int | None
    metadata: dict[str, Any]     # Default: {}
    completed_at: datetime | None
```

### GenerationCancelRequest
**Cancel task**
```python
class GenerationCancelRequest(BaseModel):
    task_id: UUID
```

### GenerationOptions
**Generation configuration**
```python
class GenerationOptions(BaseModel):
    include_infographics: bool    # Default: True
    style: str                   # Default: "professional"
    language: str                # 2-5 characters, default: "en"
    chapter_count: int | None    # 1-50 range
    words_per_chapter: int | None  # 500-10000 range
    include_toc: bool            # Default: True
    include_index: bool          # Default: False
```

**Usage:**
```python
options = GenerationOptions(
    include_infographics=True,
    style="academic",
    language="en",
    chapter_count=10,
    words_per_chapter=2000
)
```

---

## Enum Values

### BookStatus
```python
DRAFT                      # Initial state
OUTLINING                  # AI generating outline
GENERATING_CONTENT         # AI writing chapters
GENERATING_INFOGRAPHICS    # AI creating images
COMPILING_PDF              # Building PDF
UPLOADING_TO_DRIVE         # Uploading to cloud
COMPLETED                  # Success
FAILED                     # Error occurred
CANCELLED                  # User cancelled
```

### InputMethod
```python
TOPIC_DESCRIPTION          # User provides topic, AI creates outline
STRUCTURED_OUTLINE         # User provides outline, AI writes content
EXISTING_DOCUMENT          # User uploads document as base
```

### TaskStatus
```python
PENDING                    # Queued
STARTED                    # Worker picked up
PROGRESS                   # Actively processing
SUCCESS                    # Completed successfully
FAILURE                    # Failed with error
REVOKED                    # Cancelled
RETRY                      # Retrying after failure
```

---

## Common Validation Rules

### Email Validation
```python
from pydantic import EmailStr

email: EmailStr  # Validates format, requires email-validator package
```

### String Length
```python
name: str = Field(..., min_length=1, max_length=255)
```

### Numeric Range
```python
progress: int = Field(..., ge=0, le=100)  # 0-100 inclusive
```

### Nullable Fields
```python
topic: str | None = Field(default=None)
```

### Optional Fields (with default)
```python
is_active: bool = Field(default=True)
```

### Default Factory (for mutable defaults)
```python
items: list[Item] = Field(default_factory=list)
metadata: dict[str, Any] = Field(default_factory=dict)
```

---

## Custom Validators

### Title Sanitization
```python
@field_validator("title")
@classmethod
def sanitize_title(cls, v: str) -> str:
    return v.strip()
```

### Content Normalization
```python
@field_validator("content")
@classmethod
def normalize_content(cls, v: str | None) -> str | None:
    if v is None:
        return None
    return v.replace("\r\n", "\n").replace("\r", "\n")
```

### Hierarchy Validation
```python
@field_validator("children")
@classmethod
def validate_children_hierarchy(cls, v: list, info) -> list:
    parent_level = info.data.get("level", 0)
    for child in v:
        if child.level <= parent_level:
            raise ValueError(
                f"Child chapter '{child.title}' has level {child.level}, "
                f"must be greater than parent level {parent_level}"
            )
    return v
```

---

## ORM Mode (from_attributes)

All response schemas support ORM mode:

```python
class BookResponse(BaseModel):
    ...
    model_config = {"from_attributes": True}

# Usage with SQLAlchemy models
book = BookResponse.from_orm(book_model)  # Pydantic v1
book = BookResponse.model_validate(book_model)  # Pydantic v2
```

---

## Error Handling

### ValidationError
```python
from pydantic import ValidationError

try:
    user = UserCreate(
        email="invalid-email",
        name="Test",
        password="Short"
    )
except ValidationError as e:
    print(e.errors())
    # [
    #   {'loc': ('email',), 'type': 'value_error.email', ...},
    #   {'loc': ('password',), 'type': 'value_error.any_str.min_length', ...}
    # ]
```

---

## Best Practices

### 1. Use Type Hints
```python
# Good
title: str

# Bad
title  # No type hint
```

### 2. Provide Field Descriptions
```python
title: str = Field(
    ...,
    description="Title of the book",
    examples=["Introduction to AI"]
)
```

### 3. Use Appropriate Types
```python
# For dates
created_at: datetime

# For IDs
id: UUID

# For emails
email: EmailStr

# For optional strings
topic: str | None
```

### 4. Set Proper Constraints
```python
# Use ge/le for inclusive ranges
progress: int = Field(..., ge=0, le=100)

# Use gt/lt for exclusive ranges
rating: float = Field(..., gt=0, lt=5)
```

### 5. Provide Examples
```python
email: EmailStr = Field(
    ...,
    examples=["user@example.com"]
)
```

---

## Common Patterns

### Request Schema
```python
class BookCreate(BaseModel):
    # Required fields
    title: str = Field(...)
    # Optional fields
    topic: str | None = None
    # With validation
    input_method: InputMethod = Field(...)
```

### Response Schema
```python
class BookResponse(BaseModel):
    # All fields from model
    id: UUID
    title: str
    # Computed fields
    is_top_level: bool = Field(default=True)
    # ORM support
    model_config = {"from_attributes": True}
```

### Update Schema
```python
class BookUpdate(BaseModel):
    # All fields optional
    title: str | None = None
    topic: str | None = None
```

---

## Testing Schemas

### Validation Test
```python
from pydantic import ValidationError

# Should pass
user = UserCreate(
    email="user@example.com",
    name="Test User",
    password="SecurePass123!"
)

# Should fail
try:
    user = UserCreate(
        email="invalid",
        name="Test",
        password="Short"
    )
except ValidationError:
    print("Validation failed as expected")
```

### Field Validator Test
```python
chapter = ChapterCreate(
    title="  Title with spaces  ",  # Will be stripped
    chapter_number=1
)
assert chapter.title == "Title with spaces"
```

---

## Quick Checklist

- [ ] Import schemas from `app.schemas`
- [ ] Use `EmailStr` for email fields
- [ ] Add `description` to all fields
- [ ] Set `min_length`/`max_length` for strings
- [ ] Set `ge`/`le` for numeric ranges
- [ ] Use `str | None` for nullable fields
- [ ] Add `model_config = {"from_attributes": True}` to response schemas
- [ ] Use `Field(default=...)` for optional fields
- [ ] Use `Field(default_factory=...)` for mutable defaults
- [ ] Add custom validators for business logic
- [ ] Import and use enums for status fields

---

**Last Updated:** 2026-02-17
**Pydantic Version:** 2.0+
**Python Version:** 3.11+
