from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from apps.authentication.authentication import (
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    get_current_user,
    verify_token,
)
from apps.authentication.models.models import User
from apps.authentication.schemas import Token, UserCreate, UserLogin, UserRetrieve
from apps.authentication.utils import hash_password, verify_password
from apps.database import get_db
from base.route import StandardResponse

router = APIRouter()


@router.post("/register", response_model=StandardResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = (
        db.query(User)
        .filter((User.username == user.username) | (User.email == user.email))
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    # Create new user
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
        is_active=True,
        is_superuser=False,
        is_verified=False,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return StandardResponse(
        success=True,
        data={
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
        },
        message="User registered successfully",
    )


@router.post("/login")
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT tokens"""
    # Find user
    user = db.query(User).filter(User.username == user_credentials.username).first()

    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account",
        )

    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return StandardResponse(
        success=True,
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
        },
        message="Login successful",
    )


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client-side token removal)"""
    return StandardResponse(
        success=True,
        data=None,
        message="Logout successful. Please remove token from client.",
    )


@router.get("/me")
def get_me(current_user: User = Depends(get_current_active_user)):
    """Get current authenticated user"""
    return StandardResponse(
        success=True,
        data={
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "is_active": current_user.is_active,
            "is_verified": current_user.is_verified,
        },
        message="User retrieved successfully",
    )


@router.post("/refresh")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    try:
        user_id = verify_token(refresh_token)
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        # Create new access token
        new_access_token = create_access_token(data={"sub": str(user.id)})

        return StandardResponse(
            success=True,
            data={
                "access_token": new_access_token,
                "token_type": "bearer",
            },
            message="Token refreshed successfully",
        )
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.post("/change-password")
def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Change user password"""
    # Verify current password
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid current password",
        )

    # Update password
    current_user.hashed_password = hash_password(new_password)
    db.commit()

    return StandardResponse(
        success=True,
        data=None,
        message="Password changed successfully",
    )
