"""
AI Recommendation Engine Service.

Provides collaborative filtering, content-based filtering, and hybrid recommendations
for books in the Vibe PDF Platform.
"""
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

import numpy as np
from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import expression

from app.core.config import settings
from app.models import Book, BookStatus, InteractionType, User, UserInteraction


class RecommendationEngine:
    """Hybrid recommendation engine combining collaborative and content-based filtering."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.similarity_threshold = settings.RECOMMENDATION_SIMILARITY_THRESHOLD
        self.max_items = settings.RECOMMENDATION_MAX_ITEMS

    async def get_personalized_recommendations(
        self,
        user_id: uuid.UUID,
        limit: int = 10,
        exclude_book_ids: Optional[list[uuid.UUID]] = None,
    ) -> list[Book]:
        """
        Get personalized recommendations for a user.

        Combines collaborative filtering (similar users' preferences)
        with content-based filtering (book attributes).
        """
        # Get user's existing interactions
        user_interactions = await self._get_user_interactions(user_id)

        # If user has no history, return popular books
        if not user_interactions:
            return await self._get_popular_books(limit, exclude_book_ids)

        # Get collaborative filtering recommendations
        collab_recs = await self._collaborative_filtering(
            user_id, limit * 2, exclude_book_ids
        )

        # Get content-based recommendations
        content_recs = await self._content_based_filtering(
            user_id, limit * 2, exclude_book_ids
        )

        # Combine and rank recommendations
        combined = self._combine_recommendations(
            collab_recs, content_recs, user_interactions
        )

        return combined[:limit]

    async def get_similar_books(
        self,
        book_id: uuid.UUID,
        limit: int = 5,
    ) -> list[Book]:
        """Get books similar to the given book based on content and interactions."""
        # Get the source book
        result = await self.db.execute(
            select(Book).where(Book.id == book_id)
        )
        source_book = result.scalar_one_or_none()

        if not source_book:
            return []

        # Content-based similarity
        content_similar = await self._find_content_similar_books(
            source_book, limit * 2
        )

        # Collaborative similarity (books liked by similar users)
        collab_similar = await self._find_collaborative_similar_books(
            book_id, limit * 2
        )

        # Combine and rank
        similar_books = self._combine_similar_books(
            content_similar, collab_similar, book_id
        )

        return similar_books[:limit]

    async def get_popular_books(
        self,
        limit: int = 10,
        category: Optional[str] = None,
        exclude_book_ids: Optional[list[uuid.UUID]] = None,
    ) -> list[Book]:
        """Get popular books based on interaction counts."""
        return await self._get_popular_books(limit, exclude_book_ids, category)

    async def get_trending_books(
        self,
        days: int = 7,
        limit: int = 10,
    ) -> list[Book]:
        """Get trending books based on recent interactions."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Query books with most recent interactions
        query = (
            select(Book)
            .join(UserInteraction, UserInteraction.book_id == Book.id)
            .where(
                and_(
                    UserInteraction.created_at >= cutoff_date,
                    Book.status == BookStatus.COMPLETED,
                )
            )
            .group_by(Book.id)
            .order_by(func.count(UserInteraction.id).desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def _get_user_interactions(
        self, user_id: uuid.UUID
    ) -> dict[uuid.UUID, float]:
        """Get user's interaction weights."""
        query = select(UserInteraction).where(
            UserInteraction.user_id == user_id
        )

        result = await self.db.execute(query)
        interactions = result.scalars().all()

        weights = {}
        for interaction in interactions:
            weight = self._get_interaction_weight(interaction.interaction_type)
            weights[interaction.book_id] = weight

        return weights

    def _get_interaction_weight(self, interaction_type: InteractionType) -> float:
        """Get weight for each interaction type."""
        weights = {
            InteractionType.DOWNLOAD: 5.0,
            InteractionType.LIKE: 3.0,
            InteractionType.BOOKMARK: 2.5,
            InteractionType.SHARE: 2.0,
            InteractionType.VIEW: 1.0,
        }
        return weights.get(interaction_type, 1.0)

    async def _collaborative_filtering(
        self,
        user_id: uuid.UUID,
        limit: int,
        exclude_book_ids: Optional[list[uuid.UUID]] = None,
    ) -> list[tuple[Book, float]]:
        """
        Collaborative filtering using user-user similarity.

        Finds users with similar preferences and recommends books they liked.
        """
        # Get user's liked books
        user_likes_query = select(UserInteraction.book_id).where(
            and_(
                UserInteraction.user_id == user_id,
                UserInteraction.interaction_type.in_(
                    [InteractionType.LIKE, InteractionType.DOWNLOAD]
                ),
            )
        )
        result = await self.db.execute(user_likes_query)
        user_liked_books = set(result.scalars().all())

        if not user_liked_books:
            return []

        # Find users who liked similar books
        similar_users_query = (
            select(UserInteraction.user_id)
            .where(
                and_(
                    UserInteraction.book_id.in_(user_liked_books),
                    UserInteraction.interaction_type.in_(
                        [InteractionType.LIKE, InteractionType.DOWNLOAD]
                    ),
                    UserInteraction.user_id != user_id,
                )
            )
            .group_by(UserInteraction.user_id)
            .order_by(func.count(UserInteraction.id).desc())
            .limit(50)
        )
        result = await self.db.execute(similar_users_query)
        similar_user_ids = result.scalars().all()

        if not similar_user_ids:
            return []

        # Get books liked by similar users
        rec_query = (
            select(Book, func.count(UserInteraction.id).label("score"))
            .join(UserInteraction, UserInteraction.book_id == Book.id)
            .where(
                and_(
                    UserInteraction.user_id.in_(similar_user_ids),
                    UserInteraction.interaction_type.in_(
                        [InteractionType.LIKE, InteractionType.DOWNLOAD]
                    ),
                    Book.status == BookStatus.COMPLETED,
                    Book.user_id != user_id,
                )
            )
            .group_by(Book.id)
            .order_by(func.count(UserInteraction.id).desc())
            .limit(limit * 2)
        )

        # Exclude books if specified
        if exclude_book_ids:
            rec_query = rec_query.where(Book.id.not_in(exclude_book_ids))

        result = await self.db.execute(rec_query)
        return [(row[0], float(row[1])) for row in result.all()]

    async def _content_based_filtering(
        self,
        user_id: uuid.UUID,
        limit: int,
        exclude_book_ids: Optional[list[uuid.UUID]] = None,
    ) -> list[tuple[Book, float]]:
        """
        Content-based filtering using book attributes.

        Recommends books similar to ones the user has interacted with.
        """
        # Get user's interacted books
        query = (
            select(Book)
            .join(UserInteraction, UserInteraction.book_id == Book.id)
            .where(
                and_(
                    UserInteraction.user_id == user_id,
                    Book.status == BookStatus.COMPLETED,
                )
            )
            .limit(20)
        )
        result = await self.db.execute(query)
        user_books = result.scalars().all()

        if not user_books:
            return []

        # Collect tags and categories from user's books
        user_tags = set()
        user_categories = set()
        for book in user_books:
            if book.tags:
                user_tags.update(book.tags)
            if book.category:
                user_categories.add(book.category)

        # Score other books based on tag/category similarity
        category_score = case(
            (Book.category.in_(user_categories), 3.0),
            else_=0.0
        )
        tag_score = case(
            (Book.tags.overlap(list(user_tags)), 5.0),
            else_=0.0
        )

        # Build query for candidate books
        book_ids = [b.id for b in user_books]
        candidate_query = (
            select(Book, (category_score + tag_score).label("score"))
            .where(
                and_(
                    Book.id.not_in(book_ids),
                    Book.status == BookStatus.COMPLETED,
                    Book.user_id != user_id,
                )
            )
            .order_by((category_score + tag_score).desc())
            .limit(limit * 2)
        )

        if exclude_book_ids:
            candidate_query = candidate_query.where(
                Book.id.not_in(exclude_book_ids)
            )

        result = await self.db.execute(candidate_query)
        return [(row[0], float(row[1])) for row in result.all()]

    def _combine_recommendations(
        self,
        collab_recs: list[tuple[Book, float]],
        content_recs: list[tuple[Book, float]],
        user_interactions: dict[uuid.UUID, float],
    ) -> list[Book]:
        """Combine collaborative and content-based recommendations."""
        # Use weighted scoring
        collab_weight = 0.6
        content_weight = 0.4

        scores = {}

        # Add collaborative scores
        for book, score in collab_recs:
            scores[book.id] = scores.get(book.id, 0) + score * collab_weight

        # Add content-based scores
        for book, score in content_recs:
            scores[book.id] = scores.get(book.id, 0) + score * content_weight

        # Sort by score
        sorted_books = sorted(
            [(book, score) for book, score in collab_recs + content_recs 
             if book.id in scores],
            key=lambda x: scores.get(x[0].id, 0),
            reverse=True
        )

        return [book for book, _ in sorted_books]

    async def _find_content_similar_books(
        self, source_book: Book, limit: int
    ) -> list[tuple[Book, float]]:
        """Find books similar based on content attributes."""
        user_categories = {source_book.category} if source_book.category else set()
        user_tags = set(source_book.tags) if source_book.tags else set()

        if not user_categories and not user_tags:
            return []

        category_score = case(
            (Book.category.in_(user_categories), 3.0),
            else_=0.0
        )
        tag_score = case(
            (Book.tags.overlap(list(user_tags)), 5.0),
            else_=0.0
        )

        query = (
            select(Book, (category_score + tag_score).label("score"))
            .where(
                and_(
                    Book.id != source_book.id,
                    Book.status == BookStatus.COMPLETED,
                )
            )
            .order_by((category_score + tag_score).desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        return [(row[0], float(row[1])) for row in result.all()]

    async def _find_collaborative_similar_books(
        self, book_id: uuid.UUID, limit: int
    ) -> list[tuple[Book, float]]:
        """Find books similar based on user interaction patterns."""
        # Get users who liked this book
        query = select(UserInteraction.user_id).where(
            and_(
                UserInteraction.book_id == book_id,
                UserInteraction.interaction_type == InteractionType.LIKE,
            )
        )
        result = await self.db.execute(query)
        users_who_liked = result.scalars().all()

        if not users_who_liked:
            return []

        # Find other books they liked
        rec_query = (
            select(Book, func.count(UserInteraction.id).label("score"))
            .join(UserInteraction, UserInteraction.book_id == Book.id)
            .where(
                and_(
                    UserInteraction.user_id.in_(users_who_liked),
                    UserInteraction.book_id != book_id,
                    UserInteraction.interaction_type == InteractionType.LIKE,
                    Book.status == BookStatus.COMPLETED,
                )
            )
            .group_by(Book.id)
            .orderInteraction.id).desc_by(func.count(User())
            .limit(limit)
        )

        result = await self.db.execute(rec_query)
        return [(row[0], float(row[1])) for row in result.all()]

    def _combine_similar_books(
        self,
        content_similar: list[tuple[Book, float]],
        collab_similar: list[tuple[Book, float]],
        source_book_id: uuid.UUID,
    ) -> list[Book]:
        """Combine content and collaborative similar books."""
        scores = {}

        for book, score in content_similar:
            scores[book.id] = scores.get(book.id, 0) + score * 0.5

        for book, score in collab_similar:
            if book.id != source_book_id:
                scores[book.id] = scores.get(book.id, 0) + score * 0.5

        # Sort by combined score
        all_books = {b.id: b for b, _ in content_similar + collab_similar}
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

        return [all_books[bid] for bid in sorted_ids if bid in all_books]

    async def _get_popular_books(
        self,
        limit: int,
        exclude_book_ids: Optional[list[uuid.UUID]] = None,
        category: Optional[str] = None,
    ) -> list[Book]:
        """Get popular books based on total interactions."""
        query = (
            select(Book)
            .outerjoin(UserInteraction)
            .where(Book.status == BookStatus.COMPLETED)
            .group_by(Book.id)
            .order_by(func.count(UserInteraction.id).desc())
            .limit(limit)
        )

        if category:
            query = query.where(Book.category == category)

        if exclude_book_ids:
            query = query.where(Book.id.not_in(exclude_book_ids))

        result = await self.db.execute(query)
        return list(result.scalars().all())


# Service factory function
async def get_recommendation_engine(db: AsyncSession) -> RecommendationEngine:
    """Get a recommendation engine instance."""
    return RecommendationEngine(db)
