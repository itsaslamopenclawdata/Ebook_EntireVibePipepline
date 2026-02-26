"""
Natural Language Query Service.

Provides text-to-SQL translation, semantic search, and query understanding
for the Vibe PDF Platform.
"""
import re
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

import numpy as np
from sqlalchemy import and_, asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Book, BookStatus, Chapter, User


class QueryIntent(str, Enum):
    """Intent types for natural language queries."""
    LIST = "list"
    FIND = "find"
    COUNT = "count"
    FILTER = "filter"
    SEARCH = "search"
    COMPARE = "compare"
    AGGREGATE = "aggregate"


class TimeRange(str, Enum):
    """Time range filters."""
    TODAY = "today"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL = "all"


@dataclass
class QueryUnderstanding:
    """Understanding of a natural language query."""
    intent: QueryIntent
    entities: dict[str, Any]
    filters: dict[str, Any]
    sort: Optional[dict[str, str]]
    pagination: dict[str, int]
    confidence: float


@dataclass
class SearchResult:
    """Search result with relevance score."""
    book: Book
    relevance_score: float
    matched_fields: list[str]


class NLPQueryService:
    """
    Natural language query processing service.

    Translates natural language queries into SQL and provides semantic search.
    """

    # Intent patterns
    INTENT_PATTERNS = {
        QueryIntent.LIST: [
            r"^(list|show|get|display|give me)\s+(all\s+)?(my\s+)?(books?|documents?)",
        ],
        QueryIntent.FIND: [
            r"^find\s+(me\s+)?(a\s+)?(book?|document?)",
            r"^search\s+(for\s+)?(a\s+)?(book?|document?)",
            r"^(where|how)\s+can\s+I\s+find",
        ],
        QueryIntent.COUNT: [
            r"^how\s+many\s+(books?|documents?)",
            r"^count\s+(of\s+)?(the\s+)?(books?|documents?)",
        ],
        QueryIntent.FILTER: [
            r"^(filter|show|list)\s+.*\s+(by|with|that\s+are|that\s+is)",
        ],
        QueryIntent.SEARCH: [
            r"^search\s+(for\s+)?(.+)",
            r"^find\s+(.+)",
            r"^look\s+(up|for)\s+(.+)",
        ],
    }

    # Status keywords
    STATUS_KEYWORDS = {
        BookStatus.DRAFT: ["draft", "unpublished", "not started"],
        BookStatus.COMPLETED: ["completed", "finished", "done", "ready"],
        BookStatus.FAILED: ["failed", "error", "broken"],
        BookStatus.GENERATING_CONTENT: [
            "generating", "writing", "creating", "in progress"
        ],
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def understand_query(self, query: str) -> QueryUnderstanding:
        """
        Understand a natural language query.

        Extracts intent, entities, filters, and pagination from the query.
        """
        query = query.lower().strip()

        # Detect intent
        intent = self._detect_intent(query)

        # Extract entities
        entities = self._extract_entities(query)

        # Extract filters
        filters = self._extract_filters(query, entities)

        # Extract sorting
        sort = self._extract_sort(query)

        # Extract pagination
        pagination = self._extract_pagination(query)

        # Calculate confidence
        confidence = self._calculate_confidence(intent, filters)

        return QueryUnderstanding(
            intent=intent,
            entities=entities,
            filters=filters,
            sort=sort,
            pagination=pagination,
            confidence=confidence,
        )

    async def execute_query(
        self,
        query: str,
        user_id: uuid.UUID,
    ) -> dict[str, Any]:
        """
        Execute a natural language query.

        Returns results based on the understood query.
        """
        # Understand the query
        understanding = await self.understand_query(query)

        # Build and execute SQL based on intent
        if understanding.intent == QueryIntent.COUNT:
            return await self._execute_count(understanding, user_id)
        elif understanding.intent == QueryIntent.SEARCH:
            return await self._execute_search(understanding, user_id)
        else:
            return await self._execute_list(understanding, user_id)

    async def text_to_sql(
        self,
        query: str,
        user_id: uuid.UUID,
    ) -> tuple[str, dict[str, Any]]:
        """
        Convert natural language query to SQL.

        Returns the SQL query and parameters.
        """
        understanding = await self.understand_query(query)

        # Build base query
        if understanding.intent == QueryIntent.COUNT:
            base_query = select(func.count(Book.id))
            conditions = [Book.user_id == user_id]
        else:
            base_query = select(Book)
            conditions = [Book.user_id == user_id]

        # Add filters
        for field, value in understanding.filters.items():
            if hasattr(Book, field):
                column = getattr(Book, field)
                if isinstance(value, list):
                    conditions.append(column.in_(value))
                elif isinstance(value, str) and "%" in value:
                    conditions.append(column.ilike(value))
                else:
                    conditions.append(column == value)

        # Apply conditions
        if conditions:
            base_query = base_query.where(and_(*conditions))

        # Add sorting
        if understanding.sort:
            sort_field = understanding.sort.get("field", "created_at")
            sort_order = understanding.sort.get("order", "desc")

            if hasattr(Book, sort_field):
                sort_column = getattr(Book, sort_field)
                if sort_order == "asc":
                    base_query = base_query.order_by(asc(sort_column))
                else:
                    base_query = base_query.order_by(desc(sort_column))

        # Add pagination
        limit = understanding.pagination.get("limit", 20)
        offset = understanding.pagination.get("offset", 0)
        base_query = base_query.limit(limit).offset(offset)

        # Convert to SQL string (for debugging)
        sql_str = str(base_query.compile(
            compile_kwargs={"literal_binds": True}
        ))

        return sql_str, understanding.filters

    async def semantic_search(
        self,
        query: str,
        user_id: uuid.UUID,
        limit: int = 10,
    ) -> list[SearchResult]:
        """
        Perform semantic search across books and chapters.

        Uses keyword matching as a proxy for semantic search.
        For production, would use embeddings and vector similarity.
        """
        # Extract search terms
        understanding = await self.understand_query(query)

        search_terms = query.lower().split()
        search_terms = [t for t in search_terms if len(t) > 2]

        if not search_terms:
            return []

        # Search in books
        book_conditions = [
            Book.user_id == user_id,
            Book.status == BookStatus.COMPLETED,
            or_(
                Book.title.ilike(f"%{term}%")
                for term in search_terms
            ),
        ]

        book_query = select(Book).where(and_(*book_conditions))
        result = await self.db.execute(book_query)
        books = result.scalars().all()

        # Calculate relevance scores
        results = []
        for book in books:
            score = self._calculate_relevance(book, search_terms)
            matched_fields = self._get_matched_fields(book, search_terms)

            results.append(SearchResult(
                book=book,
                relevance_score=score,
                matched_fields=matched_fields,
            ))

        # Sort by relevance
        results.sort(key=lambda x: x.relevance_score, reverse=True)

        return results[:limit]

    async def generate_suggestions(
        self,
        partial_query: str,
        user_id: uuid.UUID,
    ) -> list[str]:
        """
        Generate query suggestions based on partial input.

        Provides autocomplete-like suggestions.
        """
        suggestions = []

        # Get user's recent book titles
        result = await self.db.execute(
            select(Book.title)
            .where(Book.user_id == user_id)
            .order_by(Book.created_at.desc())
            .limit(5)
        )
        recent_titles = result.scalars().all()

        # Match partial query against titles
        partial = partial_query.lower()
        for title in recent_titles:
            if title.lower().startswith(partial):
                suggestions.append(f'"{title}"')

        # Add common query patterns
        patterns = [
            f"{partial_query} my books",
            f"{partial_query} completed books",
            f"{partial_query} books from last month",
            f"show {partial_query}",
            f"find {partial_query}",
        ]

        suggestions.extend(patterns[:3])

        return suggestions[:5]

    # Private methods

    def _detect_intent(self, query: str) -> QueryIntent:
        """Detect the intent of the query."""
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    return intent

        # Default to list
        return QueryIntent.LIST

    def _extract_entities(self, query: str) -> dict[str, Any]:
        """Extract entities from the query."""
        entities = {}

        # Extract time range
        for time_range in TimeRange:
            if time_range.value in query:
                entities["time_range"] = time_range
                break

        # Extract status
        for status, keywords in self.STATUS_KEYWORDS.items():
            if any(kw in query for kw in keywords):
                entities["status"] = status
                break

        # Extract rating (if mentioned)
        rating_match = re.search(r"(\d+)\s*(?:star|point)", query)
        if rating_match:
            entities["rating"] = int(rating_match.group(1))

        return entities

    def _extract_filters(self, query: str, entities: dict[str, Any]) -> dict[str, Any]:
        """Extract filter conditions from the query."""
        filters = {}

        # Add status filter
        if "status" in entities:
            filters["["status"]

        # Add time rangestatus"] = entities filter
        if "time_range" in entities:
            filters["time_range"] = entities["time_range"]

        # Extract category
        category_match = re.search(
            r"(?:category|topic|subject|type)\s+(?:of\s+)?(.+?)(?:\s+books?|$)",
            query
        )
        if category_match:
            filters["category"] = category_match.group(1).strip()

        # Extract title keywords
        search_match = re.search(
            r"(?:called|titled|about|named)\s+(?:\"?)(.+?)(?:\"|$|<)",
            query
        )
        if search_match:
            filters["title"] = f"%{search_match.group(1).strip()}%"

        return filters

    def _extract_sort(self, query: str) -> Optional[dict[str, str]]:
        """Extract sorting from the query."""
        if any(word in query for word in ["newest", "latest", "recent"]):
            return {"field": "created_at", "order": "desc"}
        elif any(word in query for word in ["oldest", "earliest"]):
            return {"field": "created_at", "order": "asc"}
        elif "title" in query:
            return {"field": "title", "order": "asc"}

        return None

    def _extract_pagination(self, query: str) -> dict[str, int]:
        """Extract pagination from the query."""
        pagination = {"limit": 20, "offset": 0}

        # Extract limit
        limit_match = re.search(r"(?:show|list|get|find)\s+(\d+)", query)
        if limit_match:
            pagination["limit"] = int(limit_match.group(1))

        # Extract page
        page_match = re.search(r"page\s+(\d+)", query)
        if page_match:
            page = int(page_match.group(1))
            pagination["offset"] = (page - 1) * pagination["limit"]

        return pagination

    def _calculate_confidence(
        self,
        intent: QueryIntent,
        filters: dict[str, Any],
    ) -> float:
        """Calculate confidence of understanding."""
        confidence = 0.5  # Base confidence

        # Boost for filters
        confidence += len(filters) * 0.1

        # Boost for clear intent patterns
        if intent in [QueryIntent.COUNT, QueryIntent.LIST]:
            confidence += 0.2

        return min(1.0, confidence)

    async def _execute_count(
        self,
        understanding: QueryUnderstanding,
        user_id: uuid.UUID,
    ) -> dict[str, Any]:
        """Execute a count query."""
        query = select(func.count(Book.id)).where(Book.user_id == user_id)

        # Apply filters
        conditions = []
        for field, value in understanding.filters.items():
            if hasattr(Book, field):
                conditions.append(getattr(Book, field) == value)

        if conditions:
            query = query.where(and_(*conditions))

        result = await self.db.execute(query)
        count = result.scalar()

        return {"count": count, "query": understanding}

    async def _execute_list(
        self,
        understanding: QueryUnderstanding,
        user_id: uuid.UUID,
    ) -> dict[str, Any]:
        """Execute a list query."""
        query = select(Book).where(Book.user_id == user_id)

        # Apply filters
        for field, value in understanding.filters.items():
            if hasattr(Book, field):
                if isinstance(value, list):
                    query = query.where(getattr(Book, field).in_(value))
                else:
                    query = query.where(getattr(Book, field) == value)

        # Apply sorting
        if understanding.sort:
            sort_field = understanding.sort.get("field", "created_at")
            sort_order = understanding.sort.get("order", "desc")

            if hasattr(Book, sort_field):
                sort_column = getattr(Book, sort_field)
                if sort_order == "asc":
                    query = query.order_by(asc(sort_column))
                else:
                    query = query.order_by(desc(sort_column))

        # Apply pagination
        limit = understanding.pagination.get("limit", 20)
        offset = understanding.pagination.get("offset", 0)
        query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        books = result.scalars().all()

        # Get total count
        count_query = select(func.count(Book.id)).where(Book.user_id == user_id)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        return {
            "items": books,
            "total": total,
            "limit": limit,
            "offset": offset,
            "query": understanding,
        }

    async def _execute_search(
        self,
        understanding: QueryUnderstanding,
        user_id: uuid.UUID,
    ) -> dict[str, Any]:
        """Execute a search query."""
        # Extract search terms from the query
        search_query = re.sub(
            r"^(search|find|look)\s+(up|for|me)?",
            "",
            understanding.filters.get("title", "%")
        ).strip()

        if search_query == "%":
            search_query = "%"

        query = (
            select(Book)
            .where(
                and_(
                    Book.user_id == user_id,
                    Book.status == BookStatus.COMPLETED,
                    or_(
                        Book.title.ilike(f"%{search_query}%"),
                        Book.topic.ilike(f"%{search_query}%"),
                    ),
                )
            )
            .limit(understanding.pagination.get("limit", 20))
        )

        result = await self.db.execute(query)
        books = result.scalars().all()

        return {
            "items": books,
            "total": len(books),
            "query": understanding,
        }

    def _calculate_relevance(self, book: Book, search_terms: list[str]) -> float:
        """Calculate relevance score for a book."""
        score = 0.0

        # Title match (highest weight)
        if book.title:
            title_lower = book.title.lower()
            for term in search_terms:
                if term in title_lower:
                    score += 3.0

        # Topic match
        if book.topic:
            topic_lower = book.topic.lower()
            for term in search_terms:
                if term in topic_lower:
                    score += 2.0

        # Category match
        if book.category:
            category_lower = book.category.lower()
            for term in search_terms:
                if term in category_lower:
                    score += 1.5

        # Tag match
        if book.tags:
            for tag in book.tags:
                tag_lower = tag.lower()
                for term in search_terms:
                    if term in tag_lower:
                        score += 1.0

        return score

    def _get_matched_fields(
        self,
        book: Book,
        search_terms: list[str],
    ) -> list[str]:
        """Get list of fields that matched the search terms."""
        matched = []

        if book.title and any(
            term in book.title.lower() for term in search_terms
        ):
            matched.append("title")

        if book.topic and any(
            term in book.topic.lower() for term in search_terms
        ):
            matched.append("topic")

        if book.category and any(
            term in book.category.lower() for term in search_terms
        ):
            matched.append("category")

        return matched


# Service factory
async def get_nlp_query_service(db: AsyncSession) -> NLPQueryService:
    """Get an NLP query service instance."""
    return NLPQueryService(db)
