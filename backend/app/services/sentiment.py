"""
Sentiment Analysis Service.

Provides sentiment analysis for reviews, including aspect-based sentiment
and real-time analysis capabilities.
"""
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

import numpy as np
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Review


class SentimentLabel(str, Enum):
    """Sentiment labels."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


@dataclass
class AspectSentiment:
    """Sentiment for a specific aspect."""
    aspect: str
    sentiment: SentimentLabel
    confidence: float
    evidence: list[str]


@dataclass
class SentimentResult:
    """Complete sentiment analysis result."""
    overall_sentiment: SentimentLabel
    score: float  # -1.0 to 1.0
    confidence: float
    aspects: list[AspectSentiment]
    keywords: list[str]
    language: str


class SentimentAnalyzer:
    """
    Sentiment analysis service with aspect-based capabilities.

    Uses a combination of lexicon-based and ML approaches for sentiment analysis.
    """

    # Sentiment lexicons
    POSITIVE_WORDS = {
        "excellent", "amazing", "wonderful", "fantastic", "great", "good",
        "love", "loved", "best", "perfect", "beautiful", "awesome",
        "outstanding", "superb", "impressive", "helpful", "valuable",
        "recommend", "enjoyed", "satisfied", "pleased", "happy",
        "professional", "quality", "easy", "fast", "efficient"
    }

    NEGATIVE_WORDS = {
        "bad", "terrible", "awful", "horrible", "poor", "worst",
        "hate", "disappointed", "disappointing", "waste", "useless",
        "broken", "failed", "failure", "slow", "frustrating", "annoying",
        "difficult", "confusing", "complicated", "expensive", "overpriced",
        "unprofessional", "rude", "never", "avoid", "regret"
    }

    # Intensifiers
    INTENSIFIERS = {
        "very": 1.5, "really": 1.5, "extremely": 2.0, "absolutely": 2.0,
        "highly": 1.5, "incredibly": 2.0, "particularly": 1.3
    }

    # Negations
    NEGATIONS = {
        "not", "no", "never", "n't", "dont", "don't", "won't", "wouldn't",
        "couldn't", "shouldn't", "isn't", "aren't", "wasn't", "weren't"
    }

    # Aspect keywords mapping
    ASPECT_KEYWORDS = {
        "content": ["content", "writing", "words", "text", "chapters", "information"],
        "quality": ["quality", "format", "layout", "design", "presentation"],
        "value": ["value", "price", "worth", "money", "cost", "affordable"],
        "usability": ["easy", "simple", "clear", "understand", "navigate", "use"],
        "support": ["support", "help", "service", "response", "customer"],
        "speed": ["fast", "quick", "slow", "speed", "time", "download"],
        "accuracy": ["accurate", "correct", "error", "mistake", "reliable"],
        "appearance": ["look", "appearance", "cover", "visuals", "images", "beautiful"],
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def analyze_review(
        self,
        review_id: uuid.UUID,
    ) -> Optional[SentimentResult]:
        """Analyze a stored review and update its sentiment data."""
        result = await self.db.execute(
            select(Review).where(Review.id == review_id)
        )
        review = result.scalar_one_or_none()

        if not review:
            return None

        # Perform analysis
        sentiment_result = await self.analyze_text(review.content)

        # Update review with sentiment data
        review.sentiment_score = sentiment_result.score
        review.sentiment_label = sentiment_result.overall_sentiment.value
        review.aspect_sentiments = {
            aspect.aspect: {
                "sentiment": aspect.sentiment.value,
                "confidence": aspect.confidence,
            }
            for aspect in sentiment_result.aspects
        }

        await self.db.commit()

        return sentiment_result

    async def analyze_text(
        self,
        text: str,
    ) -> SentimentResult:
        """
        Analyze text for sentiment.

        Returns a complete sentiment analysis result.
        """
        # Clean and preprocess text
        cleaned_text = self._preprocess_text(text)

        # Get overall sentiment
        overall_sentiment, score, confidence = self._analyze_overall_sentiment(
            cleaned_text
        )

        # Extract keywords
        keywords = self._extract_keywords(cleaned_text)

        # Analyze aspects
        aspects = self._analyze_aspects(cleaned_text)

        # Determine language (simple heuristic)
        language = self._detect_language(cleaned_text)

        return SentimentResult(
            overall_sentiment=overall_sentiment,
            score=score,
            confidence=confidence,
            aspects=aspects,
            keywords=keywords,
            language=language,
        )

    async def batch_analyze_reviews(
        self,
        book_id: uuid.UUID,
    ) -> dict:
        """Analyze all reviews for a book and return aggregated sentiment."""
        result = await self.db.execute(
            select(Review).where(Review.book_id == book_id)
        )
        reviews = result.scalars().all()

        if not reviews:
            return {
                "total_reviews": 0,
                "average_score": 0.0,
                "sentiment_distribution": {},
                "aspect_sentiments": {},
            }

        sentiment_scores = []
        sentiment_labels = []

        for review in reviews:
            # Analyze if not already done
            if review.sentiment_score is None:
                await self.analyze_review(review.id)

            if review.sentiment_score is not None:
                sentiment_scores.append(float(review.sentiment_score))
                if review.sentiment_label:
                    sentiment_labels.append(review.sentiment_label)

        # Calculate distribution
        distribution = {}
        for label in SentimentLabel:
            distribution[label.value] = sentiment_labels.count(label.value)

        # Aggregate aspect sentiments
        aspect_aggregates = {}
        for review in reviews:
            if review.aspect_sentiments:
                for aspect, data in review.aspect_sentiments.items():
                    if aspect not in aspect_aggregates:
                        aspect_aggregates[aspect] = {"positive": 0, "negative": 0, "neutral": 0}
                    if data.get("sentiment"):
                        aspect_aggregates[aspect][data["sentiment"]] = \
                            aspect_aggregates[aspect].get(data["sentiment"], 0) + 1

        return {
            "total_reviews": len(reviews),
            "average_score": np.mean(sentiment_scores) if sentiment_scores else 0.0,
            "sentiment_distribution": distribution,
            "aspect_sentiments": aspect_aggregates,
        }

    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis."""
        # Convert to lowercase
        text = text.lower()

        # Remove URLs
        text = re.sub(r"http\S+|www\S+", "", text)

        # Remove extra whitespace
        text = " ".join(text.split())

        return text

    def _analyze_overall_sentiment(
        self, text: str
    ) -> tuple[SentimentLabel, float, float]:
        """Analyze overall sentiment of text."""
        words = text.split()
        score = 0.0
        word_count = 0
        intensifier = 1.0

        for i, word in enumerate(words):
            # Check for negation
            is_negated = i > 0 and words[i - 1] in self.NEGATIONS

            # Check for intensifier
            if word in self.INTENSIFIERS:
                intensifier = self.INTENSIFIERS[word]
                continue

            # Score word
            if word in self.POSITIVE_WORDS:
                modifier = -1 if is_negated else 1
                score += modifier * intensifier
                word_count += 1
            elif word in self.NEGATIVE_WORDS:
                modifier = 1 if is_negated else -1
                score += modifier * intensifier
                word_count += 1

            # Reset intensifier after use
            intensifier = 1.0

        # Normalize score to -1 to 1 range
        if word_count > 0:
            normalized_score = score / word_count
            normalized_score = max(-1.0, min(1.0, normalized_score))
        else:
            normalized_score = 0.0

        # Determine label
        if normalized_score > 0.1:
            label = SentimentLabel.POSITIVE
        elif normalized_score < -0.1:
            label = SentimentLabel.NEGATIVE
        else:
            label = SentimentLabel.NEUTRAL

        # Calculate confidence based on word count
        confidence = min(1.0, word_count / 10) if word_count > 0 else 0.0

        return label, normalized_score, confidence

    def _extract_keywords(self, text: str) -> list[str]:
        """Extract sentiment-relevant keywords."""
        words = text.split()

        # Get unique sentiment words
        sentiment_words = []
        for word in words:
            if word in self.POSITIVE_WORDS or word in self.NEGATIVE_WORDS:
                sentiment_words.append(word)

        # Return top keywords
        return list(set(sentiment_words))[:10]

    def _analyze_aspects(self, text: str) -> list[AspectSentiment]:
        """Analyze sentiment for specific aspects."""
        aspects = []

        for aspect_name, keywords in self.ASPECT_KEYWORDS.items():
            # Check if any keyword for this aspect appears
            aspect_sentences = []
            sentences = re.split(r"[.!?]", text)

            for sentence in sentences:
                sentence_lower = sentence.lower()
                if any(keyword in sentence_lower for keyword in keywords):
                    aspect_sentences.append(sentence.strip())

            if aspect_sentences:
                # Analyze sentiment for aspect-specific sentences
                aspect_text = " ".join(aspect_sentences)
                sentiment, score, confidence = self._analyze_overall_sentiment(
                    aspect_text
                )

                # Extract evidence (relevant sentences)
                evidence = [
                    s.strip() for s in aspect_sentences
                    if any(
                        w in s.lower() for w in
                        (self.POSITIVE_WORDS | self.NEGATIVE_WORDS)
                    )
                ][:3]

                aspects.append(AspectSentiment(
                    aspect=aspect_name,
                    sentiment=sentiment,
                    confidence=confidence,
                    evidence=evidence,
                ))

        return aspects

    def _detect_language(self, text: str) -> str:
        """Simple language detection based on common words."""
        # Simple heuristic - check for common English words
        english_common = {
            "the", "is", "at", "which", "on", "and", "a", "an", "to", "of",
            "in", "for", "with", "was", "were", "been", "have", "has", "had"
        }

        words = set(text.split())
        english_count = len(words & english_common)

        if english_count > len(words) * 0.3:
            return "en"

        return "unknown"


# Service factory
async def get_sentiment_analyzer(db: AsyncSession) -> SentimentAnalyzer:
    """Get a sentiment analyzer instance."""
    return SentimentAnalyzer(db)
