"""
Simplified Authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db_session
from app.services.auth_service import AuthService, AuthenticationError
from app.schemas.auth import (
    UserRegistrationRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
    LoginResponse,
    RegistrationResponse,
    BaseResponse,
)

logger = structlog.get_logger()

router = APIRouter()


@router.post(
    "/register",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
async def register_user(
    user_data: UserRegistrationRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Register a new user account"""
    try:
        auth_service = AuthService(db)
        
        # Register user
        user = await auth_service.register_user(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name,
            phone=user_data.phone,
            role=user_data.role
        )
        
        logger.info(
            "User registration successful",
            user_id=str(user.id),
            email=user.email
        )
        
        return RegistrationResponse(
            user=UserResponse.model_validate(user),
            message="Registration successful"
        )
        
    except AuthenticationError as e:
        logger.warning("Registration failed", error=e.message, email=user_data.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        logger.error("Registration error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="User login"
)
async def login_user(
    login_data: UserLoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Authenticate user and return access tokens"""
    try:
        auth_service = AuthService(db)
        
        # Authenticate user
        user = await auth_service.authenticate_user(
            email=login_data.email,
            password=login_data.password
        )
        
        # Create session and tokens
        access_token, refresh_token = await auth_service.create_user_session(user)
        
        logger.info(
            "User login successful",
            user_id=str(user.id),
            email=user.email
        )
        
        return LoginResponse(
            user=UserResponse.model_validate(user),
            tokens=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=30 * 60  # 30 minutes
            ),
            message="Login successful"
        )
        
    except AuthenticationError as e:
        logger.warning("Login failed", error=e.message, email=login_data.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )
    except Exception as e:
        logger.error("Login error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )


@router.get(
    "/health",
    response_model=BaseResponse,
    summary="Health check"
)
async def health_check():
    """Health check endpoint"""
    return BaseResponse(
        success=True,
        message="Auth service is healthy"
    )
