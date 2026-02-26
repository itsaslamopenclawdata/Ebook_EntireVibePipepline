"""Ebook content management endpoints."""
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.core.database import get_db
from app.core.security import get_current_user, get_current_verified_user
from app.models.user import User, Ebook, Chapter, BookStatus, UserProfileVisibility
from app.schemas.schemas import (
    EbookCreate,
    EbookUpdate,
    EbookResponse,
    EbookListResponse,
    ChapterCreate,
    ChapterUpdate,
    ChapterResponse,
    MessageResponse,
    UserPublicResponse,
)

router = APIRouter(prefix="/ebooks", tags=["Ebooks"])


# Ebook CRUD Endpoints
@router.get("", response_model=EbookListResponse)
async def list_ebooks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[BookStatus] = None,
    genre: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all published ebooks with optional filtering."""
    query = select(Ebook).where(Ebook.status == BookStatus.PUBLISHED)
    
    # Apply filters
    if status:
        query = query.where(Ebook.status == status)
    
    if genre:
        query = query.where(Ebook.genre == genre)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Ebook.title.ilike(search_term),
                Ebook.description.ilike(search_term)
            )
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination and ordering
    query = query.order_by(Ebook.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    ebooks = result.scalars().all()
    
    return EbookListResponse(
        items=[EbookResponse.model_validate(e) for e in ebooks],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/my", response_model=EbookListResponse)
async def list_my_ebooks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[BookStatus] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List current user's ebooks."""
    query = select(Ebook).where(Ebook.author_id == current_user.id)
    
    if status:
        query = query.where(Ebook.status == status)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination and ordering
    query = query.order_by(Ebook.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    ebooks = result.scalars().all()
    
    return EbookListResponse(
        items=[EbookResponse.model_validate(e) for e in ebooks],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{ebook_id}", response_model=EbookResponse)
async def get_ebook(
    ebook_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get ebook details."""
    result = await db.execute(
        select(Ebook).where(Ebook.id == ebook_id)
    )
    ebook = result.scalar_one_or_none()
    
    if not ebook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ebook not found"
        )
    
    # Increment view count for published books
    if ebook.status == BookStatus.PUBLISHED:
        ebook.view_count += 1
        await db.commit()
    
    # Include author info
    author_result = await db.execute(select(User).where(User.id == ebook.author_id))
    author = author_result.scalar_one_or_none()
    
    response = EbookResponse.model_validate(ebook)
    if author:
        response.author = UserPublicResponse(
            id=author.id,
            username=author.username,
            full_name=author.full_name,
            avatar_url=author.avatar_url,
            bio=author.bio,
            profile_visibility=author.profile_visibility,
            created_at=author.created_at
        )
    
    return response


@router.post("", response_model=EbookResponse, status_code=status.HTTP_201_CREATED)
async def create_ebook(
    ebook_data: EbookCreate,
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new ebook."""
    ebook = Ebook(
        author_id=current_user.id,
        title=ebook_data.title,
        description=ebook_data.description,
        cover_image_url=ebook_data.cover_image_url,
        content=ebook_data.content,
        genre=ebook_data.genre,
        tags=ebook_data.tags,
        status=BookStatus.DRAFT,
    )
    
    db.add(ebook)
    await db.commit()
    await db.refresh(ebook)
    
    return EbookResponse.model_validate(ebook)


@router.put("/{ebook_id}", response_model=EbookResponse)
async def update_ebook(
    ebook_id: uuid.UUID,
    ebook_data: EbookUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an ebook."""
    result = await db.execute(
        select(Ebook).where(Ebook.id == ebook_id)
    )
    ebook = result.scalar_one_or_none()
    
    if not ebook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ebook not found"
        )
    
    # Check ownership
    if ebook.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this ebook"
        )
    
    # Store previous version if content is changing
    update_data = ebook_data.model_dump(exclude_unset=True)
    
    if "content" in update_data and update_data["content"] != ebook.content:
        # Save current version
        previous_versions = ebook.previous_versions or []
        previous_versions.append({
            "version": ebook.version,
            "content": ebook.content,
            "updated_at": ebook.updated_at.isoformat() if ebook.updated_at else None
        })
        ebook.previous_versions = previous_versions
        ebook.version += 1
    
    # Update fields
    for field, value in update_data.items():
        setattr(ebook, field, value)
    
    await db.commit()
    await db.refresh(ebook)
    
    return EbookResponse.model_validate(ebook)


@router.delete("/{ebook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ebook(
    ebook_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an ebook."""
    result = await db.execute(
        select(Ebook).where(Ebook.id == ebook_id)
    )
    ebook = result.scalar_one_or_none()
    
    if not ebook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ebook not found"
        )
    
    # Check ownership
    if ebook.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this ebook"
        )
    
    await db.delete(ebook)
    await db.commit()


@router.post("/{ebook_id}/publish", response_model=EbookResponse)
async def publish_ebook(
    ebook_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Publish an ebook."""
    result = await db.execute(
        select(Ebook).where(Ebook.id == ebook_id)
    )
    ebook = result.scalar_one_or_none()
    
    if not ebook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ebook not found"
        )
    
    # Check ownership
    if ebook.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to publish this ebook"
        )
    
    # Validate required fields
    if not ebook.title or not ebook.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title and content are required for publishing"
        )
    
    ebook.status = BookStatus.PUBLISHED
    ebook.published_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(ebook)
    
    return EbookResponse.model_validate(ebook)


@router.post("/{ebook_id}/archive", response_model=EbookResponse)
async def archive_ebook(
    ebook_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Archive an ebook."""
    result = await db.execute(
        select(Ebook).where(Ebook.id == ebook_id)
    )
    ebook = result.scalar_one_or_none()
    
    if not ebook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ebook not found"
        )
    
    # Check ownership
    if ebook.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to archive this ebook"
        )
    
    ebook.status = BookStatus.ARCHIVED
    
    await db.commit()
    await db.refresh(ebook)
    
    return EbookResponse.model_validate(ebook)


# Chapter Management Endpoints
@router.get("/{ebook_id}/chapters")
async def list_chapters(
    ebook_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """List all chapters of an ebook."""
    result = await db.execute(
        select(Ebook).where(Ebook.id == ebook_id)
    )
    ebook = result.scalar_one_or_none()
    
    if not ebook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ebook not found"
        )
    
    result = await db.execute(
        select(Chapter).where(Chapter.ebook_id == ebook_id).order_by(Chapter.chapter_number)
    )
    chapters = result.scalars().all()
    
    return {
        "items": [
            {
                "id": c.id,
                "chapter_number": c.chapter_number,
                "title": c.title,
                "version": c.version,
                "created_at": c.created_at,
                "updated_at": c.updated_at
            }
            for c in chapters
        ],
        "total": len(chapters)
    }


@router.get("/{ebook_id}/chapters/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(
    ebook_id: uuid.UUID,
    chapter_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific chapter."""
    result = await db.execute(
        select(Chapter).where(
            Chapter.id == chapter_id,
            Chapter.ebook_id == ebook_id
        )
    )
    chapter = result.scalar_one_or_none()
    
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter not found"
        )
    
    return ChapterResponse.model_validate(chapter)


@router.post("/{ebook_id}/chapters", response_model=ChapterResponse, status_code=status.HTTP_201_CREATED)
async def create_chapter(
    ebook_id: uuid.UUID,
    chapter_data: ChapterCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new chapter."""
    result = await db.execute(
        select(Ebook).where(Ebook.id == ebook_id)
    )
    ebook = result.scalar_one_or_none()
    
    if not ebook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ebook not found"
        )
    
    # Check ownership
    if ebook.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add chapters to this ebook"
        )
    
    # Check if chapter number already exists
    result = await db.execute(
        select(Chapter).where(
            Chapter.ebook_id == ebook_id,
            Chapter.chapter_number == chapter_data.chapter_number
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chapter number already exists"
        )
    
    chapter = Chapter(
        ebook_id=ebook_id,
        chapter_number=chapter_data.chapter_number,
        title=chapter_data.title,
        content=chapter_data.content,
    )
    
    db.add(chapter)
    await db.commit()
    await db.refresh(chapter)
    
    return ChapterResponse.model_validate(chapter)


@router.put("/{ebook_id}/chapters/{chapter_id}", response_model=ChapterResponse)
async def update_chapter(
    ebook_id: uuid.UUID,
    chapter_id: uuid.UUID,
    chapter_data: ChapterUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a chapter."""
    result = await db.execute(
        select(Chapter).where(
            Chapter.id == chapter_id,
            Chapter.ebook_id == ebook_id
        )
    )
    chapter = result.scalar_one_or_none()
    
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter not found"
        )
    
    # Get ebook to check ownership
    result = await db.execute(select(Ebook).where(Ebook.id == ebook_id))
    ebook = result.scalar_one_or_none()
    
    if ebook.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this chapter"
        )
    
    # Store previous version if content is changing
    update_data = chapter_data.model_dump(exclude_unset=True)
    
    if "content" in update_data and update_data["content"] != chapter.content:
        previous_versions = chapter.previous_versions or []
        previous_versions.append({
            "version": chapter.version,
            "content": chapter.content,
            "updated_at": chapter.updated_at.isoformat() if chapter.updated_at else None
        })
        chapter.previous_versions = previous_versions
        chapter.version += 1
    
    # Update fields
    for field, value in update_data.items():
        setattr(chapter, field, value)
    
    await db.commit()
    await db.refresh(chapter)
    
    return ChapterResponse.model_validate(chapter)


@router.delete("/{ebook_id}/chapters/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chapter(
    ebook_id: uuid.UUID,
    chapter_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a chapter."""
    result = await db.execute(
        select(Chapter).where(
            Chapter.id == chapter_id,
            Chapter.ebook_id == ebook_id
        )
    )
    chapter = result.scalar_one_or_none()
    
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter not found"
        )
    
    # Get ebook to check ownership
    result = await db.execute(select(Ebook).where(Ebook.id == ebook_id))
    ebook = result.scalar_one_or_none()
    
    if ebook.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this chapter"
        )
    
    await db.delete(chapter)
    await db.commit()


# Version History
@router.get("/{ebook_id}/versions")
async def get_version_history(
    ebook_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get version history of an ebook."""
    result = await db.execute(
        select(Ebook).where(Ebook.id == ebook_id)
    )
    ebook = result.scalar_one_or_none()
    
    if not ebook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ebook not found"
        )
    
    # Check ownership
    if ebook.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view version history"
        )
    
    return {
        "current_version": ebook.version,
        "previous_versions": ebook.previous_versions or []
    }


@router.get("/{ebook_id}/versions/{version}")
async def get_version(
    ebook_id: uuid.UUID,
    version: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific version of an ebook."""
    result = await db.execute(
        select(Ebook).where(Ebook.id == ebook_id)
    )
    ebook = result.scalar_one_or_none()
    
    if not ebook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ebook not found"
        )
    
    # Check ownership
    if ebook.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view version"
        )
    
    # Check if requested version is current
    if version == ebook.version:
        return {
            "version": version,
            "content": ebook.content,
            "is_current": True
        }
    
    # Look in previous versions
    previous_versions = ebook.previous_versions or []
    for v in previous_versions:
        if v.get("version") == version:
            return {
                "version": version,
                "content": v.get("content"),
                "is_current": False,
                "updated_at": v.get("updated_at")
            }
    
    raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
