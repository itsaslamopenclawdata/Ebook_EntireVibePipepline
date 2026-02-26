"""Authentication endpoints."""
import uuid
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)
from app.core.config import settings
from app.models.user import User, RefreshToken, EmailVerification, PasswordReset, UserProfileVisibility
from app.schemas.schemas import (
    UserCreate,
    UserResponse,
    UserUpdate,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    EmailVerificationRequest,
    EmailVerificationConfirm,
    MessageResponse,
    UserPublicResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def generate_verification_token() -> str:
    """Generate a secure verification token."""
    return secrets.token_urlsafe(32)


def generate_password_reset_token() -> str:
    """Generate a secure password reset token."""
    return secrets.token_urlsafe(32)


async def send_verification_email(email: str, token: str):
    """Send verification email (placeholder - implement with actual email service)."""
    # TODO: Implement actual email sending
    print(f"Verification email to {email}: {settings.FRONTEND_URL}/verify-email?token={token}")


async def send_password_reset_email(email: str, token: str):
    """Send password reset email (placeholder - implement with actual email service)."""
    # TODO: Implement actual email sending
    print(f"Password reset email to {email}: {settings.FRONTEND_URL}/reset-password?token={token}")


# Registration
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists (if provided)
    if user_data.username:
        result = await db.execute(select(User).where(User.username == user_data.username))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hash_password(user_data.password),
        is_active=True,
        is_verified=False,  # Requires email verification
    )
    
    db.add(user)
    await db.flush()
    
    # Generate verification token
    verification_token = generate_verification_token()
    email_verification = EmailVerification(
        user_id=user.id,
        token=verification_token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(email_verification)
    await db.commit()
    
    # Send verification email
    await send_verification_email(user.email, verification_token)
    
    return user


# Login
@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login with email and password."""
    # Find user
    result = await db.execute(
        select(User).where(User.email == login_data.email)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Store refresh token
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(db_refresh_token)
    await db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


# Login with OAuth2 form (for Swagger UI)
@router.post("/login/oauth2", response_model=TokenResponse)
async def login_oauth2(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login with OAuth2 form (for Swagger UI)."""
    return await login(
        LoginRequest(email=form_data.username, password=form_data.password),
        db
    )


# Refresh token
@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token."""
    # Decode refresh token
    payload = decode_token(token_data.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id = payload.get("sub")
    
    # Check if token exists and is valid
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token == token_data.refresh_token,
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False
        )
    )
    stored_token = result.scalar_one_or_none()
    
    if not stored_token or stored_token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Revoke old token
    stored_token.is_revoked = True
    
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Generate new tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Store new refresh token
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token=new_refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(db_refresh_token)
    await db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token
    )


# Logout
@router.post("/logout", response_model=MessageResponse)
async def logout(
    token_data: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout and revoke refresh token."""
    # Revoke the refresh token
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token == token_data.refresh_token,
            RefreshToken.user_id == current_user.id
        )
    )
    stored_token = result.scalar_one_or_none()
    
    if stored_token:
        stored_token.is_revoked = True
        await db.commit()
    
    return MessageResponse(message="Logged out successfully")


# Request password reset
@router.post("/password-reset", response_model=MessageResponse)
async def request_password_reset(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset."""
    # Find user by email
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    # Always return success to prevent email enumeration
    if user:
        # Generate password reset token
        reset_token = generate_password_reset_token()
        password_reset = PasswordReset(
            user_id=user.id,
            token=reset_token,
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        db.add(password_reset)
        await db.commit()
        
        # Send password reset email
        await send_password_reset_email(user.email, reset_token)
    
    return MessageResponse(
        message="If the email exists, a password reset link has been sent"
    )


# Confirm password reset
@router.post("/password-reset/confirm", response_model=MessageResponse)
async def confirm_password_reset(
    request: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """Confirm password reset with new password."""
    # Find password reset token
    result = await db.execute(
        select(PasswordReset).where(
            PasswordReset.token == request.token,
            PasswordReset.is_used == False
        )
    )
    password_reset = result.scalar_one_or_none()
    
    if not password_reset:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    if password_reset.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )
    
    # Update user password
    result = await db.execute(select(User).where(User.id == password_reset.user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.hashed_password = hash_password(request.new_password)
    password_reset.is_used = True
    await db.commit()
    
    # Revoke all refresh tokens for the user
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user.id,
            RefreshToken.is_revoked == False
        )
    )
    tokens = result.scalars().all()
    for token in tokens:
        token.is_revoked = True
    await db.commit()
    
    return MessageResponse(message="Password reset successfully")


# Request email verification
@router.post("/verify-email", response_model=MessageResponse)
async def request_email_verification(
    request: EmailVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Request email verification email."""
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Generate verification token
    verification_token = generate_verification_token()
    email_verification = EmailVerification(
        user_id=current_user.id,
        token=verification_token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(email_verification)
    await db.commit()
    
    # Send verification email
    await send_verification_email(current_user.email, verification_token)
    
    return MessageResponse(message="Verification email sent")


# Confirm email verification
@router.post("/verify-email/confirm", response_model=MessageResponse)
async def confirm_email_verification(
    request: EmailVerificationConfirm,
    db: AsyncSession = Depends(get_db)
):
    """Confirm email verification."""
    # Find verification token
    result = await db.execute(
        select(EmailVerification).where(
            EmailVerification.token == request.token,
            EmailVerification.is_used == False
        )
    )
    email_verification = result.scalar_one_or_none()
    
    if not email_verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    if email_verification.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired"
        )
    
    # Update user
    result = await db.execute(select(User).where(User.id == email_verification.user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_verified = True
    email_verification.is_used = True
    await db.commit()
    
    return MessageResponse(message="Email verified successfully")


# Get current user
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information."""
    return current_user
