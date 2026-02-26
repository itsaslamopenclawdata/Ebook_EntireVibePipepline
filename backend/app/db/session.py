"""
Database session management with connection pooling.
"""
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import AsyncAdaptedQueuePool, NullPool

from app.core.config import settings


class DatabaseManager:
    """Manages database connections with connection pooling."""

    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker[AsyncSession]] = None

    @property
    def engine(self) -> AsyncEngine:
        """Get or create the database engine."""
        if self._engine is None:
            self._engine = self._create_engine()
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Get or create the session factory."""
        if self._session_factory is None:
            self._session_factory = self._create_session_factory()
        return self._session_factory

    def _create_engine(self) -> AsyncEngine:
        """Create the database engine with connection pooling."""
        # Pool configuration
        pool_size = getattr(settings, "DB_POOL_SIZE", 10)
        max_overflow = getattr(settings, "DB_MAX_OVERFLOW", 20)
        pool_timeout = getattr(settings, "DB_POOL_TIMEOUT", 30)
        pool_recycle = getattr(settings, "DB_POOL_RECYCLE", 3600)
        pool_pre_ping = getattr(settings, "DB_POOL_PRE_PING", True)

        # Check if we should use NullPool (for testing)
        use_null_pool = getattr(settings, "TESTING", False)

        engine_args = {
            "echo": getattr(settings, "DB_ECHO", False),
            "poolclass": NullPool if use_null_pool else AsyncAdaptedQueuePool,
        }

        if not use_null_pool:
            engine_args.update(
                {
                    "pool_size": pool_size,
                    "max_overflow": max_overflow,
                    "pool_timeout": pool_timeout,
                    "pool_recycle": pool_recycle,
                    "pool_pre_ping": pool_pre_ping,
                }
            )

        # Create async engine
        return create_async_engine(
            settings.DATABASE_URL,
            **engine_args,
        )

    def _create_session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Create the session factory."""
        return async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    async def create_all(self) -> None:
        """Create all tables (for development/testing)."""
        from app.models import Base

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_all(self) -> None:
        """Drop all tables (for development/testing)."""
        from app.models import Base

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def close(self) -> None:
        """Close the engine and all connections."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None


# Global database manager instance
db_manager = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database sessions.

    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with db_manager.session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions.

    Usage:
        async with get_db_context() as session:
            ...
    """
    async with db_manager.session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize the database connection pool."""
    # Prime the connection pool
    async with db_manager.engine.begin() as conn:
        # Just verify the connection works
        await conn.execute("SELECT 1")


async def health_check() -> bool:
    """Check if the database connection is healthy."""
    try:
        async with db_manager.engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception:
        return False


# Async session type for dependency injection
Session = AsyncSession
