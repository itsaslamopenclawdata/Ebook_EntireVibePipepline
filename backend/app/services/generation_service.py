"""Generation service for async book/chapter generation."""
import uuid
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.generation_task import GenerationTask, GenerationStatus, GenerationType

logger = logging.getLogger(__name__)


class GenerationService:
    """Service for managing book generation tasks."""
    
    def __init__(self, db: AsyncSession):
        """Initialize generation service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def create_task(
        self,
        user_id: uuid.UUID,
        task_type: GenerationType,
        prompt: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> GenerationTask:
        """Create a new generation task.
        
        Args:
            user_id: ID of the user
            task_type: Type of generation
            prompt: Generation prompt
            parameters: Additional parameters
            
        Returns:
            Created GenerationTask instance
        """
        task = GenerationTask(
            user_id=user_id,
            task_type=task_type,
            prompt=prompt,
            parameters=parameters or {},
            status=GenerationStatus.PENDING,
        )
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        logger.info(f"Created generation task: {task.id} (type: {task_type})")
        return task
    
    async def get_task(
        self,
        task_id: uuid.UUID,
    ) -> Optional[GenerationTask]:
        """Get a generation task by ID.
        
        Args:
            task_id: ID of the task
            
        Returns:
            GenerationTask instance or None
        """
        result = await self.db.execute(
            select(GenerationTask).where(GenerationTask.id == task_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_tasks(
        self,
        user_id: uuid.UUID,
        status: Optional[GenerationStatus] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[GenerationTask]:
        """Get tasks for a user.
        
        Args:
            user_id: ID of the user
            status: Optional status filter
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of GenerationTask instances
        """
        query = select(GenerationTask).where(GenerationTask.user_id == user_id)
        
        if status:
            query = query.where(GenerationTask.status == status)
        
        query = (
            query
            .order_by(GenerationTask.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_task_status(
        self,
        task_id: uuid.UUID,
        status: GenerationStatus,
        progress_percent: Optional[int] = None,
        current_step: Optional[str] = None,
    ) -> Optional[GenerationTask]:
        """Update task status.
        
        Args:
            task_id: ID of the task
            status: New status
            progress_percent: Progress percentage (0-100)
            current_step: Description of current step
            
        Returns:
            Updated GenerationTask or None
        """
        task = await self.get_task(task_id)
        if not task:
            return None
        
        task.status = status
        
        if progress_percent is not None:
            task.progress_percent = progress_percent
        
        if current_step:
            task.current_step = current_step
        
        # Set timestamps based on status
        if status == GenerationStatus.PROCESSING and not task.started_at:
            task.started_at = datetime.utcnow()
        elif status in (GenerationStatus.COMPLETED, GenerationStatus.FAILED, GenerationStatus.CANCELLED):
            task.completed_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(task)
        
        logger.info(f"Updated task {task_id} status to {status}")
        return task
    
    async def set_task_result(
        self,
        task_id: uuid.UUID,
        result: Optional[Dict[str, Any]] = None,
        generated_content: Optional[str] = None,
    ) -> Optional[GenerationTask]:
        """Set task result.
        
        Args:
            task_id: ID of the task
            result: Result data
            generated_content: Generated text content
            
        Returns:
            Updated GenerationTask or None
        """
        task = await self.get_task(task_id)
        if not task:
            return None
        
        task.status = GenerationStatus.COMPLETED
        task.result = result
        task.generated_content = generated_content
        task.progress_percent = 100
        task.completed_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(task)
        
        logger.info(f"Task {task_id} completed successfully")
        return task
    
    async def set_task_error(
        self,
        task_id: uuid.UUID,
        error_message: str,
    ) -> Optional[GenerationTask]:
        """Set task error.
        
        Args:
            task_id: ID of the task
            error_message: Error message
            
        Returns:
            Updated GenerationTask or None
        """
        task = await self.get_task(task_id)
        if not task:
            return None
        
        task.status = GenerationStatus.FAILED
        task.error_message = error_message
        task.completed_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(task)
        
        logger.error(f"Task {task_id} failed: {error_message}")
        return task
    
    async def cancel_task(
        self,
        task_id: uuid.UUID,
    ) -> Optional[GenerationTask]:
        """Cancel a task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Updated GenerationTask or None
        """
        task = await self.get_task(task_id)
        if not task:
            return None
        
        if task.status == GenerationStatus.PENDING:
            task.status = GenerationStatus.CANCELLED
            task.completed_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(task)
            logger.info(f"Task {task_id} cancelled")
        
        return task
    
    async def delete_task(
        self,
        task_id: uuid.UUID,
    ) -> bool:
        """Delete a task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            True if deleted
        """
        task = await self.get_task(task_id)
        if not task:
            return False
        
        await self.db.delete(task)
        await self.db.commit()
        
        logger.info(f"Deleted task {task_id}")
        return True
    
    # ========== Task Helpers ==========
    
    async def get_pending_tasks(
        self,
        limit: int = 10,
    ) -> List[GenerationTask]:
        """Get pending tasks for processing.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of pending GenerationTask instances
        """
        result = await self.db.execute(
            select(GenerationTask)
            .where(GenerationTask.status == GenerationStatus.PENDING)
            .order_by(GenerationTask.created_at)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_task_stats(
        self,
        user_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """Get generation stats for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dict with statistics
        """
        result = await self.db.execute(
            select(GenerationTask).where(GenerationTask.user_id == user_id)
        )
        tasks = list(result.scalars().all())
        
        stats = {
            "total": len(tasks),
            "pending": 0,
            "processing": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
        }
        
        for task in tasks:
            stats[task.status.value] += 1
        
        return stats


async def get_generation_service(db: AsyncSession) -> GenerationService:
    """Get generation service instance.
    
    Args:
        db: Database session
        
    Returns:
        GenerationService instance
    """
    return GenerationService(db)
