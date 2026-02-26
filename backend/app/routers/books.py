"""Books CRUD API endpoints."""
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User, Ebook, Chapter, BookStatus
from app.schemas.schemas import (
    BookCreate,
    BookUpdate,
    BookResponse,
    BookListResponse,
    ChapterCreateInBook,
    ChapterInBookResponse,
    ChapterListResponse,
    UserPublicResponse,
    BookStatusEnum,
    MessageResponse,
)

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("", response_model=BookListResponse)
async def list_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[BookStatusEnum] = Query(None, alias="status"),
    genre: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's books with optional filtering."""
    query = select(Ebook).where(Ebook.author_id == current_user.id)
    
    # Apply filters
    if status_filter:
        query = query.where(Ebook.status == status_filter)
    if genre:
        query = query.where(Ebook.genre == genre)
    if search:
        query = query.where(Ebook.title.ilike(f"%{search}%"))
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination
    query = query.order_by(Ebook.updated_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    books = result.scalars().all()
    
    # Build response with author info
    items = []
    for book in books:
        items.append(BookResponse(
            id=book.id,
            author_id=book.author_id,
            title=book.title,
            description=book.description,
            cover_image_url=book.cover_image_url,
            status=book.status,
            content=book.content,
            genre=book.genre,
            tags=book.tags or [],
            version=book.version,
            view_count=book.view_count,
            download_count=book.download_count,
            rating_average=book.rating_average,
            rating_count=book.rating_count,
            created_at=book.created_at,
            updated_at=book.updated_at,
            published_at=book.published_at,
            author=UserPublicResponse(
                id=current_user.id,
                username=current_user.username,
                full_name=current_user.full_name,
                avatar_url=current_user.avatar_url,
                bio=current_user.bio,
                profile_visibility=current_user.profile_visibility,
                created_at=current_user.created_at
            ) if current_user else None
        ))
    
    return BookListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit
    )


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new book."""
    book = Ebook(
        author_id=current_user.id,
        title=book_data.title,
        description=book_data.description,
        cover_image_url=book_data.cover_image_url,
        genre=book_data.genre,
        tags=book_data.tags if book_data.tags else [],
        content=book_data.content,
        status=BookStatus.DRAFT,
    )
    db.add(book)
    await db.commit()
    await db.refresh(book)
    
    return BookResponse(
        id=book.id,
        author_id=book.author_id,
        title=book.title,
        description=book.description,
        cover_image_url=book.cover_image_url,
        status=book.status,
        content=book.content,
        genre=book.genre,
        tags=book.tags or [],
        version=book.version,
        view_count=book.view_count,
        download_count=book.download_count,
        rating_average=book.rating_average,
        rating_count=book.rating_count,
        created_at=book.created_at,
        updated_at=book.updated_at,
        published_at=book.published_at,
        author=UserPublicResponse(
            id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name,
            avatar_url=current_user.avatar_url,
            bio=current_user.bio,
            profile_visibility=current_user.profile_visibility,
            created_at=current_user.created_at
        )
    )


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get book details."""
    result = await db.execute(
        select(Ebook).where(
            Ebook.id == book_id,
            Ebook.author_id == current_user.id
        )
    )
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    return BookResponse(
        id=book.id,
        author_id=book.author_id,
        title=book.title,
        description=book.description,
        cover_image_url=book.cover_image_url,
        status=book.status,
        content=book.content,
        genre=book.genre,
        tags=book.tags or [],
        version=book.version,
        view_count=book.view_count,
        download_count=book.download_count,
        rating_average=book.rating_average,
        rating_count=book.rating_count,
        created_at=book.created_at,
        updated_at=book.updated_at,
        published_at=book.published_at,
        author=UserPublicResponse(
            id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name,
            avatar_url=current_user.avatar_url,
            bio=current_user.bio,
            profile_visibility=current_user.profile_visibility,
            created_at=current_user.created_at
        )
    )


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: uuid.UUID,
    book_data: BookUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a book."""
    result = await db.execute(
        select(Ebook).where(
            Ebook.id == book_id,
            Ebook.author_id == current_user.id
        )
    )
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Update fields
    update_data = book_data.model_dump(exclude_unset=True)
    
    # Handle status change to published
    if "status" in update_data and update_data["status"] == BookStatusEnum.PUBLISHED:
        if book.status != BookStatus.PUBLISHED:
            book.published_at = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(book, field, value)
    
    # Increment version if content changed
    if "content" in update_data:
        book.version += 1
    
    await db.commit()
    await db.refresh(book)
    
    return BookResponse(
        id=book.id,
        author_id=book.author_id,
        title=book.title,
        description=book.description,
        cover_image_url=book.cover_image_url,
        status=book.status,
        content=book.content,
        genre=book.genre,
        tags=book.tags or [],
        version=book.version,
        view_count=book.view_count,
        download_count=book.download_count,
        rating_average=book.rating_average,
        rating_count=book.rating_count,
        created_at=book.created_at,
        updated_at=book.updated_at,
        published_at=book.published_at,
        author=UserPublicResponse(
            id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name,
            avatar_url=current_user.avatar_url,
            bio=current_user.bio,
            profile_visibility=current_user.profile_visibility,
            created_at=current_user.created_at
        )
    )


@router.delete("/{book_id}", response_model=MessageResponse)
async def delete_book(
    book_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a book."""
    result = await db.execute(
        select(Ebook).where(
            Ebook.id == book_id,
            Ebook.author_id == current_user.id
        )
    )
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    await db.delete(book)
    await db.commit()
    
    return MessageResponse(message="Book deleted successfully")


@router.get("/{book_id}/chapters", response_model=ChapterListResponse)
async def get_book_chapters(
    book_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all chapters for a book."""
    # Verify book belongs to user
    result = await db.execute(
        select(Ebook).where(
            Ebook.id == book_id,
            Ebook.author_id == current_user.id
        )
    )
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Get chapters
    result = await db.execute(
        select(Chapter)
        .where(Chapter.ebook_id == book_id)
        .order_by(Chapter.chapter_number)
    )
    chapters = result.scalars().all()
    
    items = [
        ChapterInBookResponse(
            id=ch.id,
            ebook_id=ch.ebook_id,
            chapter_number=ch.chapter_number,
            title=ch.title,
            content=ch.content,
            version=ch.version,
            created_at=ch.created_at,
            updated_at=ch.updated_at
        )
        for ch in chapters
    ]
    
    return ChapterListResponse(
        items=items,
        total=len(items)
    )


@router.post("/{book_id}/chapters", response_model=ChapterInBookResponse, status_code=status.HTTP_201_CREATED)
async def add_chapter(
    book_id: uuid.UUID,
    chapter_data: ChapterCreateInBook,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a chapter to a book."""
    # Verify book belongs to user
    result = await db.execute(
        select(Ebook).where(
            Ebook.id == book_id,
            Ebook.author_id == current_user.id
        )
    )
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Check if chapter number already exists
    result = await db.execute(
        select(Chapter).where(
            Chapter.ebook_id == book_id,
            Chapter.chapter_number == chapter_data.chapter_number
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Chapter {chapter_data.chapter_number} already exists"
        )
    
    # Create chapter
    chapter = Chapter(
        ebook_id=book_id,
        chapter_number=chapter_data.chapter_number,
        title=chapter_data.title,
        content=chapter_data.content,
    )
    db.add(chapter)
    await db.commit()
    await db.refresh(chapter)
    
    # Update book's content
    if chapter.content:
        if book.content:
            book.content += f"\n\n## {chapter_data.title}\n\n{chapter.content}"
        else:
            book.content = f"## {chapter_data.title}\n\n{chapter.content}"
        await db.commit()
    
    return ChapterInBookResponse(
        id=chapter.id,
        ebook_id=chapter.ebook_id,
        chapter_number=chapter.chapter_number,
        title=chapter.title,
        content=chapter.content,
        version=chapter.version,
        created_at=chapter.created_at,
        updated_at=chapter.updated_at
    )
