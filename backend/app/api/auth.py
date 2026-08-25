"""Authentication API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.config import settings
from app.core.security import create_access_token, get_token_expire_seconds
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.schemas.response import ApiResponse
from app.services.user_service import (
    create_user,
    authenticate_user,
    UserAlreadyExistsError,
    InvalidCredentialsError,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=ApiResponse[UserResponse], status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account.

    Raises:
        400: Email or username already exists
    """
    try:
        user = create_user(db, user_data)
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return ApiResponse(
        success=True,
        data=UserResponse.model_validate(user),
        message="Account created successfully",
    )


@router.post("/login", response_model=ApiResponse[Token])
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate with email and password and receive a JWT access token.

    Raises:
        401: Invalid credentials
    """
    try:
        user = authenticate_user(db, credentials.email, credentials.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user.id)
    return ApiResponse(
        success=True,
        data=Token(
            access_token=token,
            token_type="bearer",
            expires_in=get_token_expire_seconds(),
        ),
        message="Login successful",
    )


@router.get("/me", response_model=ApiResponse[UserResponse])
def get_me(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user's profile."""
    return ApiResponse(success=True, data=UserResponse.model_validate(current_user))


@router.post("/logout", response_model=ApiResponse)
def logout(current_user: User = Depends(get_current_user)):
    """Logout endpoint. JWT is stateless; the client discards the token."""
    return ApiResponse(success=True, message="Logged out successfully")
