"""Reading progress, bookmarks, highlights, and notes endpoints."""
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, Ebook, ReadingProgress, Bookmark, Highlight, Note, Chapter, BookStatus
from app.schemas.schemas import (
    ReadingProgressCreate,
    ReadingProgressUpdate,
    ReadingProgressResponse,
    BookmarkCreate,
    BookmarkUpdate,
    BookmarkResponse,
    HighlightCreate,
    HighlightUpdate,
    HighlightResponse,
    NoteCreate,
    NoteUpdate,
    NoteResponse,
    MessageResponse,
)

router = APIRouter(prefix="/progress", tags=["Reading Progress"])


# ==================== Reading Progress ====================
@router.get("/ebooks/{ebook_id}/progress", response_model=ReadingProgressResponse)
async def get_reading_progress(
    ebook_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get reading progress for an ebook."""
    result = await db.execute(
        select(ReadingProgress).where(
            and_(
                ReadingProgress.user_id == current_user.id,
                ReadingProgress.ebook_id == ebook_id
            )
        )
    )
    progress = result.scalar_one_or_none()
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reading progress not found"
        )
    
    return ReadingProgressResponse.model_validate(progress)


@router.post("/ebooks/{ebook_id}/progress", response_model=ReadingProgressResponse)
async def create_or_update_reading_progress(
    ebook_id: uuid.UUID,
    progress_data: ReadingProgressCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create or update reading progress."""
    # Verify ebook exists
    result = await db.execute(select(Ebook).where(Ebook.id == ebook_id))
    ebook = result.scalar_one_or_none()
    
    if not ebook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ebook not found"
        )
    
    # Check if progress already exists
    result = await db.execute(
        select(ReadingProgress).where(
            and_(
                ReadingProgress.user_id == current_user.id,
                ReadingProgress.ebook_id == ebook_id
            )
        )
    )
    progress = result.scalar_one_or_none()
    
    now = datetime.utcnow()
    
    if progress:
        # Update existing progress
        progress.progress_percent = progress_data.progress_percent
        progress.last_position = progress_data.last_position
        progress.chapter_id = progress_data.chapter_id
        progress.last_read_at = now
    else:
        # Create new progress
        progress = ReadingProgress(
            user_id=current_user.id,
            ebook_id=ebook_id,
            chapter_id=progress_data.chapter_id,
            progress_percent=progress_data.progress_percent,
            last_position=progress_data.last_position,
            last_read_at=now,
        )
        db.add(progress)
    
    await db.commit()
    await db.refresh(progress)
    
    return ReadingProgressResponse.model_validate(progress)


@router.delete("/ebooks/{ebook_id}/progress", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reading_progress(
    ebook_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete reading progress."""
    result = await db.execute(
        select(ReadingProgress).where(
            and_(
                ReadingProgress.user_id == current_user.id,
                ReadingProgress.ebook_id == ebook_id
            )
        )
    )
    progress = result.scalar_one_or_none()
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reading progress not found"
        )
    
    await db.delete(progress)
    await db.commit()


# ==================== Bookmarks ====================
@router.get("/ebooks/{ebook_id}/bookmarks")
async def list_bookmarks(
    ebook_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all bookmarks for an ebook."""
    result = await db.execute(
        select(Bookmark).where(
            and_(
                Bookmark.user_id == current_user.id,
                Bookmark.ebook_id == ebook_id
            )
        ).order_by(Bookmark.position)
    )
    bookmarks = result.scalars().all()
    
    return {
        "items": [BookmarkResponse.model_validate(b) for b in bookmarks],
        "total": len(bookmarks)
    }


@router.get("/bookmarks", response_model=ReadingProgressResponse)
async def list_all_bookmarks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all bookmarks for the current user."""
    query = select(Bookmark).where(Bookmark.user_id == current_user.id)
    
    # Get total
    total = len((await db.execute(query)).scalars().all())
    
    # Apply pagination
    query = query.order_by(Bookmark.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    bookmarks = result.scalars().all()
    
    return {
        "items": [BookmarkResponse.model_validate(b) for b in bookmarks],
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/bookmarks/{bookmark_id}", response_model=BookmarkResponse)
async def get_bookmark(
    bookmark_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific bookmark."""
    result = await db.execute(
        select(Bookmark).where(
            and_(
                Bookmark.id == bookmark_id,
                Bookmark.user_id == current_user.id
            )
        )
    )
    bookmark = result.scalar_one_or_none()
    
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )
    
    return BookmarkResponse.model_validate(bookmark)


@router.post("/ebooks/{ebook_id}/bookmarks", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    ebook_id: uuid.UUID,
    bookmark_data: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new bookmark."""
    # Verify ebook exists
    result = await db.execute(select(Ebook).where(Ebook.id == ebook_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ebook not found"
        )
    
    bookmark = Bookmark(
        user_id=current_user.id,
        ebook_id=ebook_id,
        chapter_id=bookmark_data.chapter_id,
        position=bookmark_data.position,
        note=bookmark_data.note,
        title=bookmark_data.title,
    )
    
    db.add(bookmark)
    await db.commit()
    await db.refresh(bookmark)
    
    return BookmarkResponse.model_validate(bookmark)


@router.put("/bookmarks/{bookmark_id}", response_model=BookmarkResponse)
async def update_bookmark(
    bookmark_id: uuid.UUID,
    bookmark_data: BookmarkUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a bookmark."""
    result = await db.execute(
        select(Bookmark).where(
            and_(
                Bookmark.id == bookmark_id,
                Bookmark.user_id == current_user.id
            )
        )
    )
    bookmark = result.scalar_one_or_none()
    
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )
    
    update_data = bookmark_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bookmark, field, value)
    
    await db.commit()
    await db.refresh(bookmark)
    
    return BookmarkResponse.model_validate(bookmark)


@router.delete("/bookmarks/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bookmark(
    bookmark_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a bookmark."""
    result = await db.execute(
        select(Bookmark).where(
            and_(
                Bookmark.id == bookmark_id,
                Bookmark.user_id == current_user.id
            )
        )
    )
    bookmark = result.scalar_one_or_none()
    
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )
    
    await db.delete(bookmark)
    await db.commit()


# ==================== Highlights ====================
@router.get("/ebooks/{ebook_id}/highlights")
async def list_highlights(
    ebook_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all highlights for an ebook."""
    result = await db.execute(
        select(Highlight).where(
            and_(
                Highlight.user_id == current_user.id,
                Highlight.ebook_id == ebook_id
            )
        ).order_by(Highlight.start_position)
    )
    highlights = result.scalars().all()
    
    return {
        "items": [HighlightResponse.model_validate(h) for h in highlights],
        "total": len(highlights)
    }


@router.get("/highlights", response_model=ReadingProgressResponse)
async def list_all_highlights(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all highlights for the current user."""
    query = select(Highlight).where(Highlight.user_id == current_user.id)
    
    # Get total
    total = len((await db.execute(query)).scalars().all())
    
    # Apply pagination
    query = query.order_by(Highlight.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    highlights = result.scalars().all()
    
    return {
        "items": [HighlightResponse.model_validate(h) for h in highlights],
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/highlights/{highlight_id}", response_model=HighlightResponse)
async def get_highlight(
    highlight_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific highlight."""
    result = await db.execute(
        select(Highlight).where(
            and_(
                Highlight.id == highlight_id,
                Highlight.user_id == current_user.id
            )
        )
    )
    highlight = result.scalar_one_or_none()
    
    if not highlight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Highlight not found"
        )
    
    return HighlightResponse.model_validate(highlight)


@router.post("/ebooks/{ebook_id}/highlights", response_model=HighlightResponse, status_code=status.HTTP_201_CREATED)
async def create_highlight(
    ebook_id: uuid.UUID,
    highlight_data: HighlightCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new highlight."""
    # Verify ebook exists
    result = await db.execute(select(Ebook).where(Ebook.id == ebook_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ebook not found"
        )
    
    highlight = Highlight(
        user_id=current_user.id,
        ebook_id=ebook_id,
        chapter_id=highlight_data.chapter_id,
        start_position=highlight_data.start_position,
        end_position=highlight_data.end_position,
        highlighted_text=highlight_data.highlighted_text,
        color=highlight_data.color,
        note=highlight_data.note,
    )
    
    db.add(highlight)
    await db.commit()
    await db.refresh(highlight)
    
    return HighlightResponse.model_validate(highlight)


@router.put("/highlights/{highlight_id}", response_model=HighlightResponse)
async def update_highlight(
    highlight_id: uuid.UUID,
    highlight_data: HighlightUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a highlight."""
    result = await db.execute(
        select(Highlight).where(
            and_(
                Highlight.id == highlight_id,
                Highlight.user_id == current_user.id
            )
        )
    )
    highlight = result.scalar_one_or_none()
    
    if not highlight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Highlight not found"
        )
    
    update_data = highlight_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(highlight, field, value)
    
    await db.commit()
    await db.refresh(highlight)
    
    return HighlightResponse.model_validate(highlight)


@router.delete("/highlights/{highlight_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_highlight(
    highlight_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a highlight."""
    result = await db.execute(
        select(Highlight).where(
            and_(
                Highlight.id == highlight_id,
                Highlight.user_id == current_user.id
            )
        )
    )
    highlight = result.scalar_one_or_none()
    
    if not highlight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Highlight not found"
        )
    
    await db.delete(highlight)
    await db.commit()


# ==================== Notes ====================
@router.get("/ebooks/{ebook_id}/notes")
async def list_notes(
    ebook_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all notes for an ebook."""
    result = await db.execute(
        select(Note).where(
            and_(
                Note.user_id == current_user.id,
                Note.ebook_id == ebook_id
            )
        ).order_by(Note.created_at.desc())
    )
    notes = result.scalars().all()
    
    return {
        "items": [NoteResponse.model_validate(n) for n in notes],
        "total": len(notes)
    }


@router.get("/notes", response_model=ReadingProgressResponse)
async def list_all_notes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all notes for the current user."""
    query = select(Note).where(Note.user_id == current_user.id)
    
    # Get total
    total = len((await db.execute(query)).scalars().all())
    
    # Apply pagination
    query = query.order_by(Note.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    notes = result.scalars().all()
    
    return {
        "items": [NoteResponse.model_validate(n) for n in notes],
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific note."""
    result = await db.execute(
        select(Note).where(
            and_(
                Note.id == note_id,
                Note.user_id == current_user.id
            )
        )
    )
    note = result.scalar_one_or_none()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    return NoteResponse.model_validate(note)


@router.post("/ebooks/{ebook_id}/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    ebook_id: uuid.UUID,
    note_data: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new note."""
    # Verify ebook exists
    result = await db.execute(select(Ebook).where(Ebook.id == ebook_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ebook not found"
        )
    
    note = Note(
        user_id=current_user.id,
        ebook_id=ebook_id,
        chapter_id=note_data.chapter_id,
        title=note_data.title,
        content=note_data.content,
        position=note_data.position,
    )
    
    db.add(note)
    await db.commit()
    await db.refresh(note)
    
    return NoteResponse.model_validate(note)


@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: uuid.UUID,
    note_data: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a note."""
    result = await db.execute(
        select(Note).where(
            and_(
                Note.id == note_id,
                Note.user_id == current_user.id
            )
        )
    )
    note = result.scalar_one_or_none()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    update_data = note_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)
    
    await db.commit()
    await db.refresh(note)
    
    return NoteResponse.model_validate(note)


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a note."""
    result = await db.execute(
        select(Note).where(
            and_(
                Note.id == note_id,
                Note.user_id == current_user.id
            )
        )
    )
    note = result.scalar_one_or_none()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    await db.delete(note)
    await db.commit()
