"""Book service for managing ebooks."""
import uuid
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.models.user import User, Ebook, Chapter, BookStatus
from app.core.config import settings

logger = logging.getLogger(__name__)


class BookService:
    """Service for managing ebooks and chapters."""
    
    def __init__(self, db: AsyncSession):
        """Initialize book service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    # ========== Book Operations ==========
    
    async def create_book(
        self,
        user_id: uuid.UUID,
        title: str,
        description: Optional[str] = None,
        genre: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Ebook:
        """Create a new book.
        
        Args:
            user_id: ID of the author
            title: Book title
            description: Book description
            genre: Book genre
            tags: List of tags
            
        Returns:
            Created Ebook instance
        """
        book = Ebook(
            author_id=user_id,
            title=title,
            description=description,
            genre=genre,
            tags=tags or [],
            status=BookStatus.DRAFT,
        )
        
        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book)
        
        logger.info(f"Created book: {book.id} by user {user_id}")
        return book
    
    async def get_book(
        self,
        book_id: uuid.UUID,
        load_relationships: bool = False,
    ) -> Optional[Ebook]:
        """Get a book by ID.
        
        Args:
            book_id: ID of the book
            load_relationships: Whether to load chapters and author
            
        Returns:
            Ebook instance or None
        """
        query = select(Ebook).where(Ebook.id == book_id)
        
        if load_relationships:
            query = query.options(
                selectinload(Ebook.author),
                selectinload(Ebook.chapters),
            )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_books(
        self,
        user_id: uuid.UUID,
        status: Optional[BookStatus] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Ebook]:
        """Get books by user.
        
        Args:
            user_id: ID of the author
            status: Optional status filter
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of Ebook instances
        """
        query = select(Ebook).where(Ebook.author_id == user_id)
        
        if status:
            query = query.where(Ebook.status == status)
        
        query = (
            query
            .order_by(Ebook.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_book(
        self,
        book_id: uuid.UUID,
        **kwargs,
    ) -> Optional[Ebook]:
        """Update a book.
        
        Args:
            book_id: ID of the book
            **kwargs: Fields to update
            
        Returns:
            Updated Ebook or None
        """
        book = await self.get_book(book_id)
        if not book:
            return None
        
        for key, value in kwargs.items():
            if hasattr(book, key):
                setattr(book, key, value)
        
        book.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(book)
        
        logger.info(f"Updated book: {book.id}")
        return book
    
    async def delete_book(
        self,
        book_id: uuid.UUID,
    ) -> bool:
        """Delete a book.
        
        Args:
            book_id: ID of the book
            
        Returns:
            True if deleted
        """
        book = await self.get_book(book_id)
        if not book:
            return False
        
        await self.db.delete(book)
        await self.db.commit()
        
        logger.info(f"Deleted book: {book_id}")
        return True
    
    async def publish_book(
        self,
        book_id: uuid.UUID,
    ) -> Optional[Ebook]:
        """Publish a book.
        
        Args:
            book_id: ID of the book
            
        Returns:
            Published Ebook or None
        """
        book = await self.get_book(book_id, load_relationships=True)
        if not book:
            return None
        
        book.status = BookStatus.PUBLISHED
        book.published_at = datetime.utcnow()
        book.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(book)
        
        logger.info(f"Published book: {book.id}")
        return book
    
    async def archive_book(
        self,
        book_id: uuid.UUID,
    ) -> Optional[Ebook]:
        """Archive a book.
        
        Args:
            book_id: ID of the book
            
        Returns:
            Archived Ebook or None
        """
        book = await self.get_book(book_id)
        if not book:
            return None
        
        book.status = BookStatus.ARCHIVED
        book.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(book)
        
        logger.info(f"Archived book: {book.id}")
        return book
    
    # ========== Chapter Operations ==========
    
    async def create_chapter(
        self,
        book_id: uuid.UUID,
        title: str,
        chapter_number: int,
        content: Optional[str] = None,
    ) -> Optional[Chapter]:
        """Create a new chapter.
        
        Args:
            book_id: ID of the book
            title: Chapter title
            chapter_number: Chapter number
            content: Chapter content
            
        Returns:
            Created Chapter or None (if book not found)
        """
        book = await self.get_book(book_id)
        if not book:
            return None
        
        chapter = Chapter(
            ebook_id=book_id,
            title=title,
            chapter_number=chapter_number,
            content=content,
        )
        
        self.db.add(chapter)
        
        # Update book version
        book.version += 1
        book.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(chapter)
        
        logger.info(f"Created chapter: {chapter.id} for book {book_id}")
        return chapter
    
    async def get_chapter(
        self,
        chapter_id: uuid.UUID,
    ) -> Optional[Chapter]:
        """Get a chapter by ID.
        
        Args:
            chapter_id: ID of the chapter
            
        Returns:
            Chapter instance or None
        """
        result = await self.db.execute(
            select(Chapter).where(Chapter.id == chapter_id)
        )
        return result.scalar_one_or_none()
    
    async def get_book_chapters(
        self,
        book_id: uuid.UUID,
    ) -> List[Chapter]:
        """Get all chapters for a book.
        
        Args:
            book_id: ID of the book
            
        Returns:
            List of Chapter instances
        """
        result = await self.db.execute(
            select(Chapter)
            .where(Chapter.ebook_id == book_id)
            .order_by(Chapter.chapter_number)
        )
        return list(result.scalars().all())
    
    async def update_chapter(
        self,
        chapter_id: uuid.UUID,
        **kwargs,
    ) -> Optional[Chapter]:
        """Update a chapter.
        
        Args:
            chapter_id: ID of the chapter
            **kwargs: Fields to update
            
        Returns:
            Updated Chapter or None
        """
        chapter = await self.get_chapter(chapter_id)
        if not chapter:
            return None
        
        for key, value in kwargs.items():
            if hasattr(chapter, key):
                setattr(chapter, key, value)
        
        chapter.version += 1
        chapter.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(chapter)
        
        logger.info(f"Updated chapter: {chapter.id}")
        return chapter
    
    async def delete_chapter(
        self,
        chapter_id: uuid.UUID,
    ) -> bool:
        """Delete a chapter.
        
        Args:
            chapter_id: ID of the chapter
            
        Returns:
            True if deleted
        """
        chapter = await self.get_chapter(chapter_id)
        if not chapter:
            return False
        
        # Update book version
        book = await self.get_book(chapter.ebook_id)
        if book:
            book.version += 1
            book.updated_at = datetime.utcnow()
        
        await self.db.delete(chapter)
        await self.db.commit()
        
        logger.info(f"Deleted chapter: {chapter_id}")
        return True
    
    # ========== Book Content ==========
    
    async def get_full_book_content(
        self,
        book_id: uuid.UUID,
    ) -> Optional[Dict[str, Any]]:
        """Get full book content including all chapters.
        
        Args:
            book_id: ID of the book
            
        Returns:
            Dict with book and chapters or None
        """
        book = await self.get_book(book_id, load_relationships=True)
        if not book:
            return None
        
        chapters = await self.get_book_chapters(book_id)
        
        return {
            "book": book,
            "chapters": chapters,
            "total_chapters": len(chapters),
            "content_length": sum(len(c.content or "") for c in chapters),
        }
    
    async def generate_book_pdf(
        self,
        book_id: uuid.UUID,
    ) -> Optional[bytes]:
        """Generate PDF for a book.
        
        Args:
            book_id: ID of the book
            
        Returns:
            PDF bytes or None
        """
        # This would use a PDF generation library
        # For now, return None as placeholder
        book_content = await self.get_full_book_content(book_id)
        if not book_content:
            return None
        
        # TODO: Implement PDF generation using reportlab or similar
        logger.info(f"Generating PDF for book: {book_id}")
        return None


async def get_book_service(db: AsyncSession) -> BookService:
    """Get book service instance.
    
    Args:
        db: Database session
        
    Returns:
        BookService instance
    """
    return BookService(db)
