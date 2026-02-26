"""User profile management endpoints."""
import os
import uuid
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User, UserProfileVisibility
from app.schemas.schemas import (
    UserResponse,
    UserUpdate,
    UserPublicResponse,
    MessageResponse,
)

router = APIRouter(prefix="/users", tags=["Users"])


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    return any(filename.lower().endswith(ext) for ext in allowed_extensions)


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile."""
    # Check for username uniqueness
    if user_data.username and user_data.username != current_user.username:
        result = await db.execute(select(User).where(User.username == user_data.username))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Update fields
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.post("/me/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload profile picture."""
    # Validate file
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not allowed. Use jpg, jpeg, png, gif, or webp"
        )
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"avatar_{current_user.id}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, "avatars", filename)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Save file
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)
    
    # Update user avatar URL
    avatar_url = f"/uploads/avatars/{filename}"
    current_user.avatar_url = avatar_url
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.delete("/me/avatar", response_model=UserResponse)
async def delete_avatar(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete profile picture."""
    if current_user.avatar_url:
        # Try to delete the file
        file_path = os.path.join(
            settings.UPLOAD_DIR,
            "avatars",
            os.path.basename(current_user.avatar_url)
        )
        if os.path.exists(file_path):
            os.remove(file_path)
        
        current_user.avatar_url = None
        await db.commit()
        await db.refresh(current_user)
    
    return current_user


@router.get("/me/visibility")
async def get_visibility_settings(
    current_user: User = Depends(get_current_user)
):
    """Get profile visibility settings."""
    return {
        "profile_visibility": current_user.profile_visibility.value
    }


@router.put("/me/visibility", response_model=MessageResponse)
async def update_visibility_settings(
    visibility: UserProfileVisibility,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update profile visibility settings."""
    current_user.profile_visibility = visibility
    await db.commit()
    
    return MessageResponse(message="Visibility settings updated")


@router.get("/{user_id}", response_model=UserPublicResponse)
async def get_user_profile(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a user's public profile."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check visibility
    if user.profile_visibility == UserProfileVisibility.PRIVATE:
        # Only return basic info for private users
        return UserPublicResponse(
            id=user.id,
            username=user.username,
            full_name=user.full_name if user.profile_visibility == UserProfileVisibility.PUBLIC else None,
            avatar_url=None,
            bio=None,
            profile_visibility=user.profile_visibility,
            created_at=user.created_at
        )
    
    return UserPublicResponse(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        bio=user.bio,
        profile_visibility=user.profile_visibility,
        created_at=user.created_at
    )


@router.get("/{user_id}/ebooks")
async def get_user_ebooks(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get user's public ebooks."""
    from app.models.user import Ebook, BookStatus
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check visibility
    if user.profile_visibility == UserProfileVisibility.PRIVATE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This user's profile is private"
        )
    
    # Get published ebooks
    result = await db.execute(
        select(Ebook).where(
            Ebook.author_id == user_id,
            Ebook.status == BookStatus.PUBLISHED
        ).order_by(Ebook.created_at.desc())
    )
    ebooks = result.scalars().all()
    
    return {
        "items": [
            {
                "id": e.id,
                "title": e.title,
                "description": e.description,
                "cover_image_url": e.cover_image_url,
                "genre": e.genre,
                "rating_average": e.rating_average,
                "rating_count": e.rating_count,
                "created_at": e.created_at
            }
            for e in ebooks
        ],
        "total": len(ebooks)
    }
