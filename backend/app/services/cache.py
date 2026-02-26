"""
Caching Layer Service.

Provides Redis caching with automatic invalidation and cache warming
for the Vibe PDF Platform.
"""
import hashlib
import json
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Callable, Optional

import redis.asyncio as redis
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Book, BookStatus, User

logger = logging.getLogger(__name__)


class CacheKey(str, Enum):
    """Standard cache key prefixes."""
    USER = "user"
    BOOK = "book"
    BOOKS_LIST = "books:list"
    BOOK_DETAIL = "book:detail"
    CHAPTER = "chapter"
    RECOMMENDATIONS = "recommendations"
    SEARCH = "search"
    DASHBOARD_STATS = "dashboard:stats"


class CacheTTL(int, Enum):
    """Cache TTL values in seconds."""
    SHORT = 60  # 1 minute
    MEDIUM = 300  # 5 minutes
    LONG = 3600  # 1 hour
    DAY = 86400  # 24 hours


class CacheService:
    """
    Redis caching service with invalidation and warming capabilities.
    """

    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._enabled = True

    @property
    def redis(self) -> redis.Redis:
        """Get or create Redis connection."""
        if self._redis is None:
            self._redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self._enabled:
            return None

        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")

        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = CacheTTL.MEDIUM,
    ) -> bool:
        """Set value in cache with TTL."""
        if not self._enabled:
            return False

        try:
            serialized = json.dumps(value, default=str)
            await self.redis.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        try:
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache delete pattern error for {pattern}: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.warning(f"Cache exists error for key {key}: {e}")
            return False

    async def get_ttl(self, key: str) -> int:
        """Get remaining TTL for key."""
        try:
            return await self.redis.ttl(key)
        except Exception:
            return -2

    # Key generation methods

    @staticmethod
    def generate_key(prefix: str, *args, **kwargs) -> str:
        """Generate cache key from prefix and arguments."""
        parts = [prefix]

        for arg in args:
            if arg is not None:
                parts.append(str(arg))

        for key, value in sorted(kwargs.items()):
            if value is not None:
                parts.append(f"{key}:{value}")

        return ":".join(parts)

    @staticmethod
    def generate_user_key(user_id: uuid.UUID) -> str:
        """Generate user cache key."""
        return f"{CacheKey.USER.value}:{user_id}"

    @staticmethod
    def generate_book_key(book_id: uuid.UUID) -> str:
        """Generate book cache key."""
        return f"{CacheKey.BOOK.value}:{book_id}"

    @staticmethod
    def generate_books_list_key(
        user_id: uuid.UUID,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> str:
        """Generate books list cache key."""
        return f"{CacheKey.BOOKS_LIST.value}:user:{user_id}:status:{status}:page:{page}:limit:{limit}"

    @staticmethod
    def generate_recommendations_key(user_id: uuid.UUID) -> str:
        """Generate recommendations cache key."""
        return f"{CacheKey.RECOMMENDATIONS.value}:{user_id}"

    @staticmethod
    def generate_search_key(query: str, user_id: uuid.UUID) -> str:
        """Generate search cache key."""
        query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
        return f"{CacheKey.SEARCH.value}:user:{user_id}:query:{query_hash}"

    @staticmethod
    def generate_dashboard_stats_key(user_id: uuid.UUID) -> str:
        """Generate dashboard stats cache key."""
        return f"{CacheKey.DASHBOARD_STATS.value}:{user_id}"

    # Cache invalidation methods

    async def invalidate_user(self, user_id: uuid.UUID) -> None:
        """Invalidate all cache for a user."""
        await self.delete(self.generate_user_key(user_id))
        await self.delete(self.generate_dashboard_stats_key(user_id))
        await self.delete_pattern(f"{CacheKey.RECOMMENDATIONS.value}:{user_id}*")
        await self.delete_pattern(f"{CacheKey.BOOKS_LIST.value}:user:{user_id}:*")

    async def invalidate_book(self, book_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Invalidate book cache."""
        await self.delete(self.generate_book_key(book_id))
        # Invalidate list caches
        await self.delete_pattern(f"{CacheKey.BOOKS_LIST.value}:user:{user_id}:*")
        # Invalidate recommendations
        await self.delete(self.generate_recommendations_key(user_id))
        # Invalidate dashboard
        await self.delete(self.generate_dashboard_stats_key(user_id))

    async def invalidate_all_books(self, user_id: uuid.UUID) -> None:
        """Invalidate all book caches for a user."""
        await self.delete_pattern(f"{CacheKey.BOOK.value}:*")
        await self.delete_pattern(f"{CacheKey.BOOKS_LIST.value}:user:{user_id}:*")
        await self.delete_pattern(f"{CacheKey.CHAPTER.value}:book:*")
        await self.delete(self.generate_recommendations_key(user_id))

    async def invalidate_search(self, user_id: uuid.UUID) -> None:
        """Invalidate search cache for a user."""
        await self.delete_pattern(f"{CacheKey.SEARCH.value}:user:{user_id}:*")

    # Cache warming methods

    async def warm_user_cache(self, db: AsyncSession, user_id: uuid.UUID) -> None:
        """Warm cache for user data."""
        # Get user
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user:
            await self.set(
                self.generate_user_key(user_id),
                {
                    "id": str(user.id),
                    "email": user.email,
                    "name": user.name,
                    "avatar_url": user.avatar_url,
                    "is_active": user.is_active,
                },
                ttl=CacheTTL.LONG,
            )

    async def warm_book_cache(self, db: AsyncSession, book_id: uuid.UUID) -> None:
        """Warm cache for a book."""
        result = await db.execute(
            select(Book).where(Book.id == book_id)
        )
        book = result.scalar_one_or_none()

        if book:
            await self.set(
                self.generate_book_key(book_id),
                {
                    "id": str(book.id),
                    "title": book.title,
                    "topic": book.topic,
                    "status": book.status.value,
                    "progress_percentage": book.progress_percentage,
                },
                ttl=CacheTTL.MEDIUM,
            )

    async def warm_recommendations(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        recommendations: list[Book],
    ) -> None:
        """Warm cache for user recommendations."""
        await self.set(
            self.generate_recommendations_key(user_id),
            [
                {
                    "id": str(book.id),
                    "title": book.title,
                    "topic": book.topic,
                    "status": book.status.value,
                }
                for book in recommendations
            ],
            ttl=CacheTTL.MEDIUM,
        )

    async def warm_dashboard_stats(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> None:
        """Warm cache for dashboard statistics."""
        # Get book counts by status
        result = await db.execute(
            select(Book.status, func.count(Book.id))
            .where(Book.user_id == user_id)
            .group_by(Book.status)
        )

        stats = {row[0].value: row[1] for row in result.all()}

        # Get total books
        total_query = select(func.count(Book.id)).where(Book.user_id == user_id)
        total_result = await db.execute(total_query)
        stats["total"] = total_result.scalar()

        await self.set(
            self.generate_dashboard_stats_key(user_id),
            stats,
            ttl=CacheTTL.SHORT,
        )

    async def warm_popular_books(
        self,
        books: list[Book],
        category: Optional[str] = None,
    ) -> None:
        """Warm cache for popular books."""
        key = f"popular:books:{category or 'all'}"
        await self.set(
            key,
            [
                {
                    "id": str(book.id),
                    "title": book.title,
                    "topic": book.topic,
                    "status": book.status.value,
                }
                for book in books
            ],
            ttl=CacheTTL.LONG,
        )


# Cache decorator
def cached(
    key_prefix: str,
    ttl: int = CacheTTL.MEDIUM,
    skip_cache_param: Optional[str] = None,
):
    """
    Decorator for caching function results.

    Usage:
        @cached("user", ttl=CacheTTL.LONG)
        async def get_user(user_id: uuid.UUID) -> User:
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_service: Optional[CacheService] = kwargs.pop("_cache_service", None)

            if cache_service is None:
                return await func(*args, **kwargs)

            # Skip cache if requested
            if skip_cache_param and kwargs.get(skip_cache_param):
                return await func(*args, **kwargs)

            # Generate cache key
            cache_key = cache_service.generate_key(
                key_prefix,
                *[arg for arg in args if not isinstance(arg, AsyncSession)],
                **{k: v for k, v in kwargs.items()
                   if k != skip_cache_param and not isinstance(v, AsyncSession)}
            )

            # Try to get from cache
            cached_value = await cache_service.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            if result is not None:
                await cache_service.set(cache_key, result, ttl)

            return result

        return wrapper
    return decorator


# Global cache service instance
cache_service = CacheService()


# Helper function for dependency injection
async def get_cache_service() -> CacheService:
    """Get cache service instance."""
    return cache_service


# Import func for database count
from sqlalchemy import func
