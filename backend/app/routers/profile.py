"""User profile API endpoints."""
import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserProfileVisibility, Ebook, ReadingProgress, Chapter, Review
from app.schemas.schemas import (
    ProfileResponse,
    ProfileUpdate,
    ReadingPreferences,
    ReadingPreferencesUpdate,
    ActivityItem,
    ActivityListResponse,
    UserProfileVisibilityEnum,
    UserPublicResponse,
    MessageResponse,
)

router = APIRouter(prefix="/profile", tags=["Profile"])

# In-memory preferences storage (use database in production)
user_preferences = {}


@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile."""
    return ProfileResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
        bio=current_user.bio,
        profile_visibility=current_user.profile_visibility,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        is_superuser=current_user.is_superuser,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


@router.put("", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile."""
    # Check for username uniqueness
    if profile_data.username and profile_data.username != current_user.username:
        result = await db.execute(select(User).where(User.username == profile_data.username))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Check for email uniqueness
    if profile_data.email and profile_data.email != current_user.email:
        result = await db.execute(select(User).where(User.email == profile_data.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Update fields
    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    return ProfileResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
        bio=current_user.bio,
        profile_visibility=current_user.profile_visibility,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        is_superuser=current_user.is_superuser,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


@router.get("/preferences", response_model=ReadingPreferences)
async def get_reading_preferences(
    current_user: User = Depends(get_current_user)
):
    """Get user's reading preferences."""
    prefs = user_preferences.get(str(current_user.id))
    if not prefs:
        # Return default preferences
        return ReadingPreferences(
            preferred_genres=[],
            font_size=None,
            theme=None,
            reading_speed_wpm=None,
            auto_scroll=False
        )
    return prefs


@router.put("/preferences", response_model=ReadingPreferences)
async def update_reading_preferences(
    prefs_data: ReadingPreferencesUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update user's reading preferences."""
    user_id = str(current_user.id)
    
    # Get existing or create default
    if user_id in user_preferences:
        existing = user_preferences[user_id]
        existing_dict = existing.model_dump()
    else:
        existing_dict = {
            "preferred_genres": [],
            "font_size": None,
            "theme": None,
            "reading_speed_wpm": None,
            "auto_scroll": False
        }
    
    # Update with provided values
    update_data = prefs_data.model_dump(exclude_unset=True)
    existing_dict.update(update_data)
    
    # Create new preferences object
    user_preferences[user_id] = ReadingPreferences(**existing_dict)
    
    return user_preferences[user_id]


@router.get("/activity", response_model=ActivityListResponse)
async def get_user_activity(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's reading and writing activity."""
    activities = []
    
    # Get reading progress activities
    result = await db.execute(
        select(ReadingProgress)
        .where(ReadingProgress.user_id == current_user.id)
        .order_by(ReadingProgress.last_read_at.desc())
        .limit(limit)
    )
    progress_items = result.scalars().all()
    
    # Get book info for each progress item
    for progress in progress_items:
        # Get book title
        book_result = await db.execute(
            select(Ebook).where(Ebook.id == progress.ebook_id)
        )
        book = book_result.scalar_one_or_none()
        
        chapter_title = None
        if progress.chapter_id:
            chapter_result = await db.execute(
                select(Chapter).where(Chapter.id == progress.chapter_id)
            )
            chapter = chapter_result.scalar_one_or_none()
            if chapter:
                chapter_title = chapter.title
        
        if book:
            activities.append(ActivityItem(
                id=progress.id,
                activity_type="reading",
                book_id=book.id,
                book_title=book.title,
                chapter_id=progress.chapter_id,
                chapter_title=chapter_title,
                description=f"Read {book.title} - {progress.progress_percent}% complete",
                created_at=progress.last_read_at
            ))
    
    # Get review activities
    result = await db.execute(
        select(Review)
        .where(Review.user_id == current_user.id)
        .order_by(Review.created_at.desc())
        .limit(limit)
    )
    review_items = result.scalars().all()
    
    for review in review_items:
        # Get book title
        book_result = await db.execute(
            select(Ebook).where(Ebook.id == review.ebook_id)
        )
        book = book_result.scalar_one_or_none()
        
        if book:
            activities.append(ActivityItem(
                id=review.id,
                activity_type="review",
                book_id=book.id,
                book_title=book.title,
                chapter_id=None,
                chapter_title=None,
                description=f"Reviewed {book.title} - {review.rating}/5 stars",
                created_at=review.created_at
            ))
    
    # Get book creation activities
    result = await db.execute(
        select(Ebook)
        .where(Ebook.author_id == current_user.id)
        .order_by(Ebook.created_at.desc())
        .limit(limit)
    )
    ebook_items = result.scalars().all()
    
    for ebook in ebook_items:
        activities.append(ActivityItem(
            id=ebook.id,
            activity_type="created",
            book_id=ebook.id,
            book_title=ebook.title,
            chapter_id=None,
            chapter_title=None,
            description=f"Created book: {ebook.title}",
            created_at=ebook.created_at
        ))
    
    # Sort all activities by date
    activities.sort(key=lambda x: x.created_at, reverse=True)
    
    # Apply pagination
    total = len(activities)
    paginated_activities = activities[skip:skip + limit]
    
    return ActivityListResponse(
        items=paginated_activities,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user statistics."""
    # Count books
    result = await db.execute(
        select(Ebook).where(Ebook.author_id == current_user.id)
    )
    books = result.scalars().all()
    total_books = len(books)
    published_books = sum(1 for b in books if b.status.value == "published")
    draft_books = sum(1 for b in books if b.status.value == "draft")
    
    # Count reviews given
    result = await db.execute(
        select(Review).where(Review.user_id == current_user.id)
    )
    reviews_given = len(result.scalars().all())
    
    # Count reading progress entries
    result = await db.execute(
        select(ReadingProgress).where(ReadingProgress.user_id == current_user.id)
    )
    reading_entries = len(result.scalars().all())
    
    # Total words written
    total_words = sum(len((b.content or "").split()) for b in books)
    
    return {
        "books": {
            "total": total_books,
            "published": published_books,
            "draft": draft_books
        },
        "reviews_given": reviews_given,
        "reading_entries": reading_entries,
        "total_words_written": total_words,
        "member_since": current_user.created_at,
        "last_active": current_user.last_login or current_user.updated_at
    }
