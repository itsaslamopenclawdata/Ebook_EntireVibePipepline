"""Celery tasks for book generation."""
import logging
from typing import Optional, Dict, Any
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.generation_task import GenerationTask, GenerationStatus, GenerationType

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "book_generation",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Database session for tasks
SyncSessionLocal = sessionmaker(
    bind=create_engine(settings.DATABASE_URL, pool_pre_ping=True),
    autocommit=False,
    autoflush=False,
)


def get_db_session():
    """Get a database session for tasks."""
    return SyncSessionLocal()


# ========== Task Helpers ==========

def update_task_status_sync(
    session,
    task_id: str,
    status: GenerationStatus,
    progress_percent: Optional[int] = None,
    current_step: Optional[str] = None,
):
    """Synchronous helper to update task status."""
    task = session.query(GenerationTask).filter(GenerationTask.id == task_id).first()
    if task:
        task.status = status
        if progress_percent is not None:
            task.progress_percent = progress_percent
        if current_step:
            task.current_step = current_step
        session.commit()


def set_task_result_sync(
    session,
    task_id: str,
    result: Optional[Dict[str, Any]] = None,
    generated_content: Optional[str] = None,
):
    """Synchronous helper to set task result."""
    task = session.query(GenerationTask).filter(GenerationTask.id == task_id).first()
    if task:
        task.status = GenerationStatus.COMPLETED
        task.result = result
        task.generated_content = generated_content
        task.progress_percent = 100
        session.commit()


def set_task_error_sync(
    session,
    task_id: str,
    error_message: str,
):
    """Synchronous helper to set task error."""
    task = session.query(GenerationTask).filter(GenerationTask.id == task_id).first()
    if task:
        task.status = GenerationStatus.FAILED
        task.error_message = error_message
        session.commit()


# ========== Generation Tasks ==========

@celery_app.task(bind=True, name="generate_full_book")
def generate_full_book(self, task_id: str, user_id: str, prompt: str, parameters: Dict[str, Any]):
    """Generate a full book based on a prompt.
    
    Args:
        task_id: ID of the generation task
        user_id: ID of the user
        prompt: Generation prompt
        parameters: Generation parameters
        
    Returns:
        Dict with generated content
    """
    logger.info(f"Starting full book generation for task {task_id}")
    
    session = get_db_session()
    try:
        # Update status to processing
        update_task_status_sync(
            session, task_id, GenerationStatus.PROCESSING,
            progress_percent=5, current_step="Initializing generation"
        )
        
        # Simulate generation process (replace with actual AI logic)
        # Step 1: Generate outline
        update_task_status_sync(
            session, task_id, GenerationStatus.PROCESSING,
            progress_percent=20, current_step="Generating book outline"
        )
        
        # TODO: Replace with actual AI generation using Anthropic/OpenAI
        outline = f"Outline for: {prompt[:100]}..."
        
        # Step 2: Generate chapters
        num_chapters = parameters.get("num_chapters", 10)
        chapters = []
        
        for i in range(num_chapters):
            chapter_num = i + 1
            update_task_status_sync(
                session, task_id, GenerationStatus.PROCESSING,
                progress_percent=20 + (chapter_num * 60 // num_chapters),
                current_step=f"Generating chapter {chapter_num}/{num_chapters}"
            )
            
            # Simulated chapter generation
            chapter_content = f"Chapter {chapter_num}: Generated content based on prompt..."
            chapters.append({
                "number": chapter_num,
                "title": f"Chapter {chapter_num}",
                "content": chapter_content,
            })
        
        # Step 3: Compile book
        update_task_status_sync(
            session, task_id, GenerationStatus.PROCESSING,
            progress_percent=90, current_step="Compiling book"
        )
        
        full_content = "\n\n".join(
            f"{ch['title']}\n\n{ch['content']}" for ch in chapters
        )
        
        # Set result
        result = {
            "outline": outline,
            "num_chapters": num_chapters,
            "total_words": len(full_content.split()),
        }
        
        set_task_result_sync(
            session, task_id, result=result, generated_content=full_content
        )
        
        logger.info(f"Book generation completed for task {task_id}")
        return result
        
    except Exception as e:
        logger.error(f"Book generation failed for task {task_id}: {e}")
        set_task_error_sync(session, task_id, str(e))
        raise
    finally:
        session.close()


@celery_app.task(bind=True, name="generate_chapter")
def generate_chapter(self, task_id: str, user_id: str, book_id: str, prompt: str, parameters: Dict[str, Any]):
    """Generate a chapter for a book.
    
    Args:
        task_id: ID of the generation task
        user_id: ID of the user
        book_id: ID of the book
        prompt: Generation prompt
        parameters: Generation parameters
        
    Returns:
        Dict with generated content
    """
    logger.info(f"Starting chapter generation for task {task_id}")
    
    session = get_db_session()
    try:
        # Update status to processing
        update_task_status_sync(
            session, task_id, GenerationStatus.PROCESSING,
            progress_percent=10, current_step="Generating chapter content"
        )
        
        # Simulate chapter generation
        # TODO: Replace with actual AI generation
        update_task_status_sync(
            session, task_id, GenerationStatus.PROCESSING,
            progress_percent=50, current_step="Writing chapter"
        )
        
        chapter_content = f"Generated chapter based on: {prompt}"
        
        # Set result
        result = {
            "book_id": book_id,
            "content": chapter_content,
            "word_count": len(chapter_content.split()),
        }
        
        set_task_result_sync(
            session, task_id, result=result, generated_content=chapter_content
        )
        
        logger.info(f"Chapter generation completed for task {task_id}")
        return result
        
    except Exception as e:
        logger.error(f"Chapter generation failed for task {task_id}: {e}")
        set_task_error_sync(session, task_id, str(e))
        raise
    finally:
        session.close()


@celery_app.task(bind=True, name="generate_summary")
def generate_summary(self, task_id: str, user_id: str, content: str, parameters: Dict[str, Any]):
    """Generate a summary of content.
    
    Args:
        task_id: ID of the generation task
        user_id: ID of the user
        content: Content to summarize
        parameters: Generation parameters
        
    Returns:
        Dict with summary
    """
    logger.info(f"Starting summary generation for task {task_id}")
    
    session = get_db_session()
    try:
        # Update status to processing
        update_task_status_sync(
            session, task_id, GenerationStatus.PROCESSING,
            progress_percent=10, current_step="Analyzing content"
        )
        
        # Simulate summarization
        # TODO: Replace with actual AI summarization
        summary_length = parameters.get("length", "medium")
        
        word_count = len(content.split())
        
        if summary_length == "short":
            summary = f"Short summary of {word_count} word document..."
        elif summary_length == "long":
            summary = f"Detailed summary of {word_count} word document with extensive analysis..."
        else:
            summary = f"Summary of {word_count} word document..."
        
        update_task_status_sync(
            session, task_id, GenerationStatus.PROCESSING,
            progress_percent=80, current_step="Finalizing summary"
        )
        
        # Set result
        result = {
            "original_word_count": word_count,
            "summary_word_count": len(summary.split()),
            "length": summary_length,
        }
        
        set_task_result_sync(
            session, task_id, result=result, generated_content=summary
        )
        
        logger.info(f"Summary generation completed for task {task_id}")
        return result
        
    except Exception as e:
        logger.error(f"Summary generation failed for task {task_id}: {e}")
        set_task_error_sync(session, task_id, str(e))
        raise
    finally:
        session.close()


@celery_app.task(bind=True, name="generate_outline")
def generate_outline(self, task_id: str, user_id: str, prompt: str, parameters: Dict[str, Any]):
    """Generate a book outline.
    
    Args:
        task_id: ID of the generation task
        user_id: ID of the user
        prompt: Generation prompt
        parameters: Generation parameters
        
    Returns:
        Dict with outline
    """
    logger.info(f"Starting outline generation for task {task_id}")
    
    session = get_db_session()
    try:
        # Update status to processing
        update_task_status_sync(
            session, task_id, GenerationStatus.PROCESSING,
            progress_percent=10, current_step="Creating outline structure"
        )
        
        # Simulate outline generation
        # TODO: Replace with actual AI outline generation
        num_chapters = parameters.get("num_chapters", 10)
        
        outline = {
            "title": f"Book outline: {prompt[:50]}",
            "chapters": [
                {"number": i + 1, "title": f"Chapter {i + 1}: Topic {i + 1}"}
                for i in range(num_chapters)
            ],
            "estimated_words": num_chapters * 2000,
        }
        
        update_task_status_sync(
            session, task_id, GenerationStatus.PROCESSING,
            progress_percent=80, current_step="Finalizing outline"
        )
        
        # Set result
        set_task_result_sync(
            session, task_id, result=outline
        )
        
        logger.info(f"Outline generation completed for task {task_id}")
        return outline
        
    except Exception as e:
        logger.error(f"Outline generation failed for task {task_id}: {e}")
        set_task_error_sync(session, task_id, str(e))
        raise
    finally:
        session.close()


# ========== Utility Tasks ==========

@celery_app.task(name="cleanup_expired_sessions")
def cleanup_expired_sessions():
    """Clean up expired user sessions."""
    from app.models.user_session import UserSession
    from datetime import datetime
    
    session = get_db_session()
    try:
        # Delete expired sessions
        deleted = session.query(UserSession).filter(
            UserSession.expires_at < datetime.utcnow()
        ).delete()
        
        session.commit()
        logger.info(f"Cleaned up {deleted} expired sessions")
        return {"deleted": deleted}
    except Exception as e:
        logger.error(f"Session cleanup failed: {e}")
        session.rollback()
        raise
    finally:
        session.close()


@celery_app.task(name="process_pending_generations")
def process_pending_generations():
    """Process pending generation tasks."""
    session = get_db_session()
    try:
        # Get pending tasks
        pending_tasks = session.query(GenerationTask).filter(
            GenerationTask.status == GenerationStatus.PENDING
        ).order_by(GenerationTask.created_at).limit(10).all()
        
        processed = 0
        for task in pending_tasks:
            try:
                # Route to appropriate task
                if task.task_type == GenerationType.FULL_BOOK:
                    generate_full_book.delay(
                        str(task.id),
                        str(task.user_id),
                        task.prompt or "",
                        task.parameters or {},
                    )
                elif task.task_type == GenerationType.CHAPTER:
                    generate_chapter.delay(
                        str(task.id),
                        str(task.user_id),
                        "",
                        task.prompt or "",
                        task.parameters or {},
                    )
                elif task.task_type == GenerationType.SUMMARY:
                    generate_summary.delay(
                        str(task.id),
                        str(task.user_id),
                        task.prompt or "",
                        task.parameters or {},
                    )
                elif task.task_type == GenerationType.OUTLINE:
                    generate_outline.delay(
                        str(task.id),
                        str(task.user_id),
                        task.prompt or "",
                        task.parameters or {},
                    )
                
                processed += 1
            except Exception as e:
                logger.error(f"Failed to queue task {task.id}: {e}")
        
        logger.info(f"Processed {processed} pending generation tasks")
        return {"processed": processed}
    finally:
        session.close()
