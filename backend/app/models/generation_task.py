"""Generation task models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class GenerationStatus(str, enum.Enum):
    """Generation task status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GenerationType(str, enum.Enum):
    """Type of generation."""
    FULL_BOOK = "full_book"
    CHAPTER = "chapter"
    SUMMARY = "summary"
    OUTLINE = "outline"


class GenerationTask(Base):
    """Generation task model for async book generation."""
    __tablename__ = "generation_tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Task details
    task_type = Column(SQLEnum(GenerationType), nullable=False)
    status = Column(SQLEnum(GenerationStatus), default=GenerationStatus.PENDING)
    
    # Input parameters
    prompt = Column(Text, nullable=True)
    parameters = Column(JSONB, default=dict)
    
    # Output
    result = Column(JSONB, nullable=True)
    generated_content = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Progress tracking
    progress_percent = Column(Integer, default=0)
    current_step = Column(String(255), nullable=True)
    
    # Celery task ID for tracking
    celery_task_id = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
