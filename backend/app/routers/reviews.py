"""Review and rating system endpoints."""
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from app.core.database select, and import get_db
from app.core.security import get_current_user
from app.models.user import User, Ebook, Review, ReviewReaction, BookStatus
from app.schemas.schemas import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    ReviewListResponse,
    ReviewReactionCreate,
    ReviewReactionResponse,
    MessageResponse,
)

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("", response_model=ReviewListResponse)
async def list_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    ebook_id: Optional[uuid.UUID] = None,
    rating: Optional[int] = Query(None, ge=1, le=5),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List reviews (user's own reviews or all approved reviews)."""
    query = select(Review)
    
    # Filter by ebook if provided
    if ebook_id:
        query = query.where(Review.ebook_id == ebook_id)
    
    # Get user's own reviews or approved reviews
    query = query.where(
        or_(
            Review.user_id == current_user.id,
            Review.is_approved == True
        )
    )
    
    # Filter by rating if provided
    if rating:
        query = query.where(Review.rating == rating)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination and ordering
    query = query.order_by(Review.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    reviews = result.scalars().all()
    
    # Build response with user info and reaction counts
    items = []
    for review in reviews:
        # Get user info
        user_result = await db.execute(select(User).where(User.id == review.user_id))
        user = user_result.scalar_one_or_none()
        
        # Get reaction counts
        helpful_count = len([r for r in review.reactions if r.reaction_type == "helpful"])
        funny_count = len([r for r in review.reactions if r.reaction_type == "funny"])
        insightful_count = len([r for r in review.reactions if r.reaction_type == "insightful"])
        
        review_response = ReviewResponse(
            id=review.id,
            ebook_id=review.ebook_id,
            user_id=review.user_id,
            rating=review.rating,
            title=review.title,
            content=review.content,
            is_approved=review.is_approved,
            is_featured=review.is_featured,
            created_at=review.created_at,
            updated_at=review.updated_at,
            helpful_count=helpful_count,
            funny_count=funny_count,
            insightful_count= insightful_count
        )
        
        if user:
            from app.schemas.schemas import UserPublicResponse
            review_response.user = UserPublicResponse(
                id=user.id,
                username=user.username,
                full_name=user.full_name,
                avatar_url=user.avatar_url,
                bio=user.bio,
                profile_visibility=user.profile_visibility,
                created_at=user.created_at
            )
        
        items.append(review_response)
    
    return ReviewListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/my-reviews", response_model=ReviewListResponse)
async def list_my_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List current user's reviews."""
    query = select(Review).where(Review.user_id == current_user.id)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination and ordering
    query = query.order_by(Review.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    reviews = result.scalars().all()
    
    return ReviewListResponse(
        items=[ReviewResponse.model_validate(r) for r in reviews],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific review."""
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Check if user can view (owner or approved)
    if review.user_id != current_user.id and not review.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Review not available"
        )
    
    # Get user info
    user_result = await db.execute(select(User).where(User.id == review.user_id))
    user = user_result.scalar_one_or_none()
    
    # Get reaction counts
    helpful_count = len([r for r in review.reactions if r.reaction_type == "helpful"])
    funny_count = len([r for r in review.reactions if r.reaction_type == "funny"])
    insightful_count = len([r for r in review.reactions if r.reaction_type == "insightful"])
    
    response = ReviewResponse(
        id=review.id,
        ebook_id=review.ebook_id,
        user_id=review.user_id,
        rating=review.rating,
        title=review.title,
        content=review.content,
        is_approved=review.is_approved,
        is_featured=review.is_featured,
        created_at=review.created_at,
        updated_at=review.updated_at,
        helpful_count=helpful_count,
        funny_count=funny_count,
        insightful_count=insightful_count
    )
    
    if user:
        from app.schemas.schemas import UserPublicResponse
        response.user = UserPublicResponse(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            avatar_url=user.avatar_url,
            bio=user.bio,
            profile_visibility=user.profile_visibility,
            created_at=user.created_at
        )
    
    return response


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new review."""
    # Verify ebook exists and is published
    result = await db.execute(select(Ebook).where(Ebook.id == review_data.ebook_id))
    ebook = result.scalar_one_or_none()
    
    if not ebook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ebook not found"
        )
    
    if ebook.status != BookStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only review published ebooks"
        )
    
    # Check if user already reviewed this ebook
    result = await db.execute(
        select(Review).where(
            and_(
                Review.ebook_id == review_data.ebook_id,
                Review.user_id == current_user.id
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this ebook"
        )
    
    # Check if user is the author
    if ebook.author_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot review your own ebook"
        )
    
    review = Review(
        ebook_id=review_data.ebook_id,
        user_id=current_user.id,
        rating=review_data.rating,
        title=review_data.title,
        content=review_data.content,
        is_approved=True,  # Auto-approve for now
    )
    
    db.add(review)
    
    # Update ebook rating
    await update_ebook_rating(ebook, db)
    
    await db.commit()
    await db.refresh(review)
    
    return ReviewResponse(
        id=review.id,
        ebook_id=review.ebook_id,
        user_id=review.user_id,
        rating=review.rating,
        title=review.title,
        content=review.content,
        is_approved=review.is_approved,
        is_featured=review.is_featured,
        created_at=review.created_at,
        updated_at=review.updated_at,
        helpful_count=0,
        funny_count=0,
        insightful_count=0
    )


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: uuid.UUID,
    review_data: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a review."""
    result = await db.execute(
        select(Review).where(
            and_(
                Review.id == review_id,
                Review.user_id == current_user.id
            )
        )
    )
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Store old rating for update
    old_rating = review.rating
    
    # Update fields
    update_data = review_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)
    
    # Update ebook rating if rating changed
    if "rating" in update_data and update_data["rating"] != old_rating:
        result = await db.execute(select(Ebook).where(Ebook.id == review.ebook_id))
        ebook = result.scalar_one_or_none()
        if ebook:
            await update_ebook_rating(ebook, db)
    
    await db.commit()
    await db.refresh(review)
    
    return ReviewResponse(
        id=review.id,
        ebook_id=review.ebook_id,
        user_id=review.user_id,
        rating=review.rating,
        title=review.title,
        content=review.content,
        is_approved=review.is_approved,
        is_featured=review.is_featured,
        created_at=review.created_at,
        updated_at=review.updated_at,
        helpful_count=len([r for r in review.reactions if r.reaction_type == "helpful"]),
        funny_count=len([r for r in review.reactions if r.reaction_type == "funny"]),
        insightful_count=len([r for r in review.reactions if r.reaction_type == "insightful"])
    )


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a review."""
    result = await db.execute(
        select(Review).where(
            and_(
                Review.id == review_id,
                Review.user_id == current_user.id
            )
        )
    )
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Update ebook rating before deletion
    result = await db.execute(select(Ebook).where(Ebook.id == review.ebook_id))
    ebook = result.scalar_one_or_none()
    if ebook:
        await db.delete(review)
        await update_ebook_rating(ebook, db)
    else:
        await db.delete(review)
    
    await db.commit()


# ==================== Review Reactions ====================
@router.post("/{review_id}/reactions", response_model=ReviewReactionResponse, status_code=status.HTTP_201_CREATED)
async def add_reaction(
    review_id: uuid.UUID,
    reaction_data: ReviewReactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a reaction to a review."""
    # Get review
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    if not review.is_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot react to unapproved review"
        )
    
    # Check if user already reacted with the same type
    result = await db.execute(
        select(ReviewReaction).where(
            and_(
                ReviewReaction.review_id == review_id,
                ReviewReaction.user_id == current_user.id,
                ReviewReaction.reaction_type == reaction_data.reaction_type
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reacted with this type"
        )
    
    # Remove existing reaction of different type (toggle)
    result = await db.execute(
        select(ReviewReaction).where(
            and_(
                ReviewReaction.review_id == review_id,
                ReviewReaction.user_id == current_user.id
            )
        )
    )
    existing_reactions = result.scalars().all()
    for existing in existing_reactions:
        if existing.reaction_type != reaction_data.reaction_type:
            await db.delete(existing)
    
    # Create new reaction
    reaction = ReviewReaction(
        review_id=review_id,
        user_id=current_user.id,
        reaction_type=reaction_data.reaction_type,
    )
    
    db.add(reaction)
    await db.commit()
    await db.refresh(reaction)
    
    return ReviewReactionResponse(
        id=reaction.id,
        review_id=reaction.review_id,
        user_id=reaction.user_id,
        reaction_type=reaction.reaction_type,
        created_at=reaction.created_at
    )


@router.delete("/{review_id}/reactions/{reaction_type}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_reaction(
    review_id: uuid.UUID,
    reaction_type: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a reaction from a review."""
    result = await db.execute(
        select(ReviewReaction).where(
            and_(
                ReviewReaction.review_id == review_id,
                ReviewReaction.user_id == current_user.id,
                ReviewReaction.reaction_type == reaction_type
            )
        )
    )
    reaction = result.scalar_one_or_none()
    
    if not reaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reaction not found"
        )
    
    await db.delete(reaction)
    await db.commit()


# ==================== Review Moderation (Admin) ====================
@router.post("/{review_id}/approve", response_model=ReviewResponse)
async def approve_review(
    review_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Approve a review (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    review.is_approved = True
    await db.commit()
    await db.refresh(review)
    
    return ReviewResponse(
        id=review.id,
        ebook_id=review.ebook_id,
        user_id=review.user_id,
        rating=review.rating,
        title=review.title,
        content=review.content,
        is_approved=review.is_approved,
        is_featured=review.is_featured,
        created_at=review.created_at,
        updated_at=review.updated_at,
        helpful_count=len([r for r in review.reactions if r.reaction_type == "helpful"]),
        funny_count=len([r for r in review.reactions if r.reaction_type == "funny"]),
        insightful_count=len([r for r in review.reactions if r.reaction_type == "insightful"])
    )


@router.post("/{review_id}/reject", response_model=ReviewResponse)
async def reject_review(
    review_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Reject a review (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    review.is_approved = False
    
    # Update ebook rating
    result = await db.execute(select(Ebook).where(Ebook.id == review.ebook_id))
    ebook = result.scalar_one_or_none()
    if ebook:
        await update_ebook_rating(ebook, db)
    
    await db.commit()
    await db.refresh(review)
    
    return ReviewResponse(
        id=review.id,
        ebook_id=review.ebook_id,
        user_id=review.user_id,
        rating=review.rating,
        title=review.title,
        content=review.content,
        is_approved=review.is_approved,
        is_featured=review.is_featured,
        created_at=review.created_at,
        updated_at=review.updated_at,
        helpful_count=0,
        funny_count=0,
        insightful_count=0
    )


@router.post("/{review_id}/feature", response_model=ReviewResponse)
async def feature_review(
    review_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Feature/unfeature a review (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    review.is_featured = not review.is_featured
    await db.commit()
    await db.refresh(review)
    
    return ReviewResponse(
        id=review.id,
        ebook_id=review.ebook_id,
        user_id=review.user_id,
        rating=review.rating,
        title=review.title,
        content=review.content,
        is_approved=review.is_approved,
        is_featured=review.is_featured,
        created_at=review.created_at,
        updated_at=review.updated_at,
        helpful_count=len([r for r in review.reactions if r.reaction_type == "helpful"]),
        funny_count=len([r for r in review.reactions if r.reaction_type == "funny"]),
        insightful_count=len([r for r in review.reactions if r.reaction_type == "insightful"])
    )


# ==================== Helper Functions ====================
async def update_ebook_rating(ebook: Ebook, db: AsyncSession):
    """Update ebook's average rating and count."""
    result = await db.execute(
        select(func.avg(Review.rating), func.count()).where(
            and_(
                Review.ebook_id == ebook.id,
                Review.is_approved == True
            )
        )
    )
    row = result.first()
    
    if row[0] is not None:
        ebook.rating_average = float(row[0])
        ebook.rating_count = row[1]
    else:
        ebook.rating_average = 0.0
        ebook.rating_count = 0
    
    await db.commit()
