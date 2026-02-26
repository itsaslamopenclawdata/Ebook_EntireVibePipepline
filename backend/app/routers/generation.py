"""Book generation API endpoints."""
import uuid
import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User, Ebook, BookStatus
from app.schemas.schemas import (
    GenerationRequest,
    GenerationStartResponse,
    GenerationProgressResponse,
    GenerationCancelResponse,
    GenerationRetryResponse,
    GenerationStatusEnum,
    GenerationProgressResponse,
    MessageResponse,
    ErrorResponse,
)

router = APIRouter(prefix="/generation", tags=["Generation"])


# In-memory storage for generation tasks (in production, use Redis/Celery)
generation_tasks = {}


async def generate_book_content(book_id: uuid.UUID, generation_id: uuid.UUID, request: GenerationRequest):
    """Background task to generate book content."""
    try:
        # Update status to processing
        generation_tasks[generation_id]["status"] = GenerationStatusEnum.PROCESSING
        generation_tasks[generation_id]["started_at"] = datetime.utcnow()
        
        total_chapters = request.chapter_count or 10
        target_words = request.target_word_count
        words_per_chapter = target_words // total_chapters
        
        from app.core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            # Get book
            result = await db.execute(select(Ebook).where(Ebook.id == book_id))
            book = result.scalar_one_or_none()
            
            if not book:
                generation_tasks[generation_id]["status"] = GenerationStatusEnum.FAILED
                generation_tasks[generation_id]["error_message"] = "Book not found"
                return
            
            # Simulate chapter-by-chapter generation
            for chapter_num in range(1, total_chapters + 1):
                # Check if cancelled
                if generation_tasks[generation_id].get("cancelled"):
                    generation_tasks[generation_id]["status"] = GenerationStatusEnum.CANCELLED
                    return
                
                # Update progress
                progress = int((chapter_num / total_chapters) * 100)
                generation_tasks[generation_id]["progress_percent"] = progress
                generation_tasks[generation_id]["current_chapter"] = chapter_num
                generation_tasks[generation_id]["total_chapters"] = total_chapters
                
                # Simulate content generation (in production, call LLM here)
                chapter_content = f"Chapter {chapter_num} content generated for {book.title}..."
                
                # Add chapter to book content
                if book.content:
                    book.content += f"\n\n## Chapter {chapter_num}\n\n{chapter_content}"
                else:
                    book.content = f"## Chapter {chapter_num}\n\n{chapter_content}"
                
                # Simulate processing time
                await asyncio.sleep(1)
            
            # Mark as completed
            generation_tasks[generation_id]["status"] = GenerationStatusEnum.COMPLETED
            generation_tasks[generation_id]["progress_percent"] = 100
            generation_tasks[generation_id]["completed_at"] = datetime.utcnow()
            
            # Update book
            await db.commit()
            
    except Exception as e:
        generation_tasks[generation_id]["status"] = GenerationStatusEnum.FAILED
        generation_tasks[generation_id]["error_message"] = str(e)


@router.post("/start", response_model=GenerationStartResponse, status_code=status.HTTP_201_CREATED)
async def start_book_generation(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start book generation process."""
    # Create book entry first
    book = Ebook(
        author_id=current_user.id,
        title=request.title,
        description=request.description,
        genre=request.genre,
        tags=request.tags if request.tags else [],
        content="",
        status=BookStatus.DRAFT,
    )
    db.add(book)
    await db.flush()
    
    # Create generation task record
    generation_id = uuid.uuid4()
    generation_tasks[generation_id] = {
        "book_id": book.id,
        "status": GenerationStatusEnum.PENDING,
        "progress_percent": 0,
        "current_chapter": None,
        "total_chapters": request.chapter_count,
        "error_message": None,
        "started_at": None,
        "completed_at": None,
        "cancelled": False,
        "created_at": datetime.utcnow(),
    }
    
    # Start background generation
    background_tasks.add_task(
        generate_book_content,
        book.id,
        generation_id,
        request
    )
    
    return GenerationStartResponse(
        generation_id=generation_id,
        book_id=book.id,
        status=GenerationStatusEnum.PENDING,
        message="Book generation started"
    )


@router.get("/progress/{book_id}", response_model=GenerationProgressResponse)
async def get_generation_progress(
    book_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get generation progress for a book."""
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
    
    # Find generation task
    generation = None
    for gen_id, gen_data in generation_tasks.items():
        if gen_data["book_id"] == book_id:
            generation = gen_data
            generation["id"] = gen_id
            break
    
    if not generation:
        # No active generation, check if book has content
        if book.content:
            return GenerationProgressResponse(
                id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                book_id=book_id,
                status=GenerationStatusEnum.COMPLETED,
                progress_percent=100,
                current_chapter=None,
                total_chapters=None,
                error_message=None,
                started_at=None,
                completed_at=None,
                created_at=book.created_at
            )
        return GenerationProgressResponse(
            id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
            book_id=book_id,
            status=GenerationStatusEnum.PENDING,
            progress_percent=0,
            current_chapter=None,
            total_chapters=None,
            error_message=None,
            started_at=None,
            completed_at=None,
            created_at=book.created_at
        )
    
    return GenerationProgressResponse(
        id=generation.get("id", uuid.UUID("00000000-0000-0000-0000-000000000000")),
        book_id=generation["book_id"],
        status=generation["status"],
        progress_percent=generation["progress_percent"],
        current_chapter=generation.get("current_chapter"),
        total_chapters=generation.get("total_chapters"),
        error_message=generation.get("error_message"),
        started_at=generation.get("started_at"),
        completed_at=generation.get("completed_at"),
        created_at=generation.get("created_at", datetime.utcnow())
    )


@router.post("/cancel/{book_id}", response_model=GenerationCancelResponse)
async def cancel_book_generation(
    book_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel an ongoing book generation."""
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
    
    # Find and cancel generation task
    generation = None
    for gen_id, gen_data in generation_tasks.items():
        if gen_data["book_id"] == book_id:
            generation = gen_data
            generation["cancelled"] = True
            generation["status"] = GenerationStatusEnum.CANCELLED
            break
    
    if not generation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active generation found for this book"
        )
    
    return GenerationCancelResponse(
        message="Book generation cancelled",
        status=GenerationStatusEnum.CANCELLED
    )


@router.post("/retry/{book_id}", response_model=GenerationRetryResponse)
async def retry_book_generation(
    book_id: uuid.UUID,
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retry a failed book generation."""
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
    
    # Check if there's a failed generation
    generation = None
    for gen_id, gen_data in generation_tasks.items():
        if gen_data["book_id"] == book_id:
            if gen_data["status"] == GenerationStatusEnum.FAILED:
                generation = gen_data
                # Remove old generation
                del generation_tasks[gen_id]
                break
    
    # Create new generation task
    generation_id = uuid.uuid4()
    generation_tasks[generation_id] = {
        "book_id": book_id,
        "status": GenerationStatusEnum.PENDING,
        "progress_percent": 0,
        "current_chapter": None,
        "total_chapters": request.chapter_count,
        "error_message": None,
        "started_at": None,
        "completed_at": None,
        "cancelled": False,
        "created_at": datetime.utcnow(),
    }
    
    # Clear book content for regeneration
    book.content = ""
    await db.commit()
    
    # Start background generation
    background_tasks.add_task(
        generate_book_content,
        book_id,
        generation_id,
        request
    )
    
    return GenerationRetryResponse(
        generation_id=generation_id,
        book_id=book_id,
        status=GenerationStatusEnum.PENDING,
        message="Book generation retry started"
    )
