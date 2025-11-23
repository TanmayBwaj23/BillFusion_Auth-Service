"""
Simplified Authentication service with JWT
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import secrets

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.core.config import settings
from app.models.user import User
from app.schemas.auth import TokenResponse, UserResponse

logger = structlog.get_logger()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthenticationError(Exception):
    """Custom authentication exception"""
    def __init__(self, message: str, error_code: str = "AUTH_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class AuthService:
    """Simplified authentication service"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    # Password Management
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        password_bytes = password.encode('utf-8')[:72]
        password_truncated = password_bytes.decode('utf-8', errors='ignore')
        return pwd_context.hash(password_truncated)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        password_bytes = plain_password.encode('utf-8')[:72]
        password_truncated = password_bytes.decode('utf-8', errors='ignore')
        return pwd_context.verify(password_truncated, hashed_password)
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate a cryptographically secure random token"""
        return secrets.token_urlsafe(length)
    
    # JWT Token Management
    def create_access_token(
        self,
        user: User,
        expires_delta: Optional[timedelta] = None
    ) -> Tuple[str, datetime]:
        """Create JWT access token"""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "name": user.name,
            "iat": datetime.now(timezone.utc),
            "exp": expire,
            "jti": self.generate_secure_token(16),
            "iss": settings.PROJECT_NAME,
            "aud": "billfusion-api",
            "type": "access"
        }
        
        encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt, expire
    
    def create_refresh_token(
        self,
        user: User,
        expires_delta: Optional[timedelta] = None
    ) -> Tuple[str, datetime]:
        """Create JWT refresh token"""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        
        payload = {
            "sub": str(user.id),
            "iat": datetime.now(timezone.utc),
            "exp": expire,
            "jti": self.generate_secure_token(16),
            "iss": settings.PROJECT_NAME,
            "aud": "billfusion-api",
            "type": "refresh"
        }
        
        encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt, expire
    
    def verify_token(self, token: str) -> dict:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                audience="billfusion-api",
                issuer=settings.PROJECT_NAME
            )
            return payload
        except JWTError as e:
            logger.warning("Token verification failed", error=str(e))
            raise AuthenticationError("Invalid token", "INVALID_TOKEN")
    
    async def get_current_user(self, token: str) -> User:
        """Get current user from JWT token"""
        try:
            payload = self.verify_token(token)
            user_id = payload.get("sub")
            if user_id is None:
                raise AuthenticationError("Invalid token payload", "INVALID_TOKEN")
            
            # Get user from database
            stmt = select(User).where(User.id == user_id)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user is None:
                raise AuthenticationError("User not found", "USER_NOT_FOUND")
            
            return user
            
        except JWTError:
            raise AuthenticationError("Invalid token", "INVALID_TOKEN")
    
    # User Registration and Authentication
    async def register_user(
        self,
        email: str,
        password: str,
        name: str,
        phone: Optional[str] = None,
        role: str = "employee"
    ) -> User:
        """Register a new user"""
        # Check if user already exists
        stmt = select(User).where(User.email == email.lower())
        result = await self.db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise AuthenticationError("Email already registered", "EMAIL_EXISTS")
        
        # Create new user
        hashed_password = self.hash_password(password)
        user = User(
            email=email.lower(),
            password=hashed_password,
            name=name,
            phone=phone,
            role=role,
            is_social_login=False
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        logger.info("User registered successfully", user_id=str(user.id), email=email)
        
        return user
    
    async def authenticate_user(
        self,
        email: str,
        password: str
    ) -> User:
        """Authenticate user with email and password"""
        # Get user from database
        stmt = select(User).where(User.email == email.lower())
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise AuthenticationError("Invalid credentials", "INVALID_CREDENTIALS")
        
        # Check if user has a password (not social login only)
        if not user.password:
            raise AuthenticationError("Please login with social provider", "NO_PASSWORD")
        
        # Verify password
        if not self.verify_password(password, user.password):
            raise AuthenticationError("Invalid credentials", "INVALID_CREDENTIALS")
        
        logger.info("User authenticated successfully", user_id=str(user.id), email=email)
        
        return user
    
    async def create_user_session(
        self,
        user: User
    ) -> Tuple[str, str]:
        """Create user session and return tokens"""
        # Create tokens
        access_token, access_expires = self.create_access_token(user)
        refresh_token, refresh_expires = self.create_refresh_token(user)
        
        logger.info("User session created", user_id=str(user.id))
        
        return access_token, refresh_token
    
    async def refresh_access_token(self, refresh_token: str) -> Tuple[str, str]:
        """Refresh access token using refresh token"""
        try:
            payload = self.verify_token(refresh_token)
            
            if payload.get("type") != "refresh":
                raise AuthenticationError("Invalid token type", "INVALID_TOKEN_TYPE")
            
            user_id = payload.get("sub")
            
            # Get user
            stmt = select(User).where(User.id == user_id)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                raise AuthenticationError("User not found", "USER_NOT_FOUND")
            
            # Create new access token
            new_access_token, _ = self.create_access_token(user)
            
            logger.info("Access token refreshed", user_id=str(user.id))
            
            return new_access_token, refresh_token
            
        except JWTError:
            raise AuthenticationError("Invalid refresh token", "INVALID_REFRESH_TOKEN")
    
    # Google OAuth
    async def authenticate_google_oauth(
        self,
        authorization_code: str,
        redirect_uri: str
    ) -> User:
        """Authenticate user with Google OAuth"""
        try:
            import httpx
            from google.oauth2 import id_token
            from google.auth.transport import requests
            
            # Exchange authorization code for tokens
            token_data = await self._exchange_google_code(authorization_code, redirect_uri)
            
            # Verify ID token
            user_info = self._verify_google_id_token(token_data["id_token"])
            
            # Find or create user
            user = await self._find_or_create_google_user(user_info)
            
            logger.info("Google OAuth authentication successful", user_id=str(user.id))
            
            return user
            
        except Exception as e:
            logger.error("Google OAuth authentication failed", error=str(e))
            raise AuthenticationError("OAuth authentication failed", "OAUTH_ERROR")
    
    async def _exchange_google_code(self, code: str, redirect_uri: str) -> dict:
        """Exchange Google authorization code for tokens"""
        import httpx
        
        token_url = "https://oauth2.googleapis.com/token"
        
        data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            
            if response.status_code != 200:
                raise AuthenticationError("Failed to exchange authorization code")
            
            return response.json()
    
    def _verify_google_id_token(self, id_token_str: str) -> dict:
        """Verify Google ID token"""
        from google.oauth2 import id_token
        from google.auth.transport import requests
        
        try:
            # Verify the token
            id_info = id_token.verify_oauth2_token(
                id_token_str,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
            
            # Verify the issuer
            if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer')
            
            return id_info
            
        except ValueError as e:
            raise AuthenticationError(f"Invalid ID token: {str(e)}")
    
    async def _find_or_create_google_user(self, user_info: dict) -> User:
        """Find existing user or create new one from Google user info"""
        email = user_info.get("email")
        
        if not email:
            raise AuthenticationError("Email not provided by Google")
        
        # Try to find existing user
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            # Update Google info if needed
            if user.is_social_login:
                user.name = f"{user_info.get('given_name', '')} {user_info.get('family_name', '')}".strip()
            return user
        
        # Create new user
        user = User(
            email=email,
            name=f"{user_info.get('given_name', '')} {user_info.get('family_name', '')}".strip() or email.split('@')[0],
            is_social_login=True
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        logger.info("New Google user created", user_id=str(user.id), email=email)
        
        return user
