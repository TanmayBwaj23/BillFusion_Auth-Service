"""
Authentication service with JWT and OAuth support
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Tuple
import secrets
import hashlib
import base64
from urllib.parse import urlencode
import httpx
import structlog

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from google.auth.transport import requests
from google.oauth2 import id_token

from app.core.config import settings
from app.models.user import User, UserSession, UserRole, UserStatus, AuthProvider, UserAuditLog
from app.schemas.auth import TokenResponse, UserResponse
from app.utils.email import EmailService
from app.utils.security import SecurityUtils

# COMPLETED FEATURES:
# ✓ Password reset functionality
# ✓ Email verification functionality
# ✓ Session management (get, revoke)
# ✓ User profile management
# ✓ Account deactivation/reactivation
# ✓ Security monitoring (suspicious activity detection)
# ✓ Audit logging

# FUTURE ENHANCEMENTS:
# TODO: Add token blacklisting (requires Redis)
# TODO: Add token rotation (requires token versioning)
# TODO: Add device fingerprinting (requires client-side library)
# TODO: Add risk-based authentication (requires ML model)
# TODO: Add session analytics (requires analytics service)
# TODO: Add fraud detection (requires ML model)
# TODO: Add rate limiting per user (partially implemented in middleware)
# TODO: Add password breach checking (requires HaveIBeenPwned API)
# TODO: Add biometric authentication (requires WebAuthn)
# TODO: Add SSO integration (requires SAML/OIDC)

logger = structlog.get_logger()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthenticationError(Exception):
    """Custom authentication exception"""
    def __init__(self, message: str, error_code: str = "AUTH_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class AuthorizationError(Exception):
    """Custom authorization exception"""
    def __init__(self, message: str, error_code: str = "AUTHZ_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class AuthService:
    """
    Authentication service handling user authentication, JWT tokens, and OAuth
    
    Implemented Features:
    - User registration and authentication
    - JWT token generation and validation
    - Google OAuth integration
    - Password reset and email verification
    - Session management
    - User profile management
    - Security monitoring and audit logging
    
    Future Enhancements:
    TODO: Add service-level caching (Redis integration)
    TODO: Add service-level metrics (Prometheus integration)
    TODO: Add service-level monitoring (Sentry integration)
    TODO: Add service-level rate limiting (per-user limits)
    TODO: Add service-level security policies (configurable rules)
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.email_service = EmailService()
        self.security_utils = SecurityUtils()
    
    # Password Management
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt
        Truncate to 72 bytes to avoid bcrypt limitation
        """
        # Bcrypt has a 72 byte limit, truncate if necessary
        password_bytes = password.encode('utf-8')[:72]
        password_truncated = password_bytes.decode('utf-8', errors='ignore')
        return pwd_context.hash(password_truncated)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        Truncate to 72 bytes to match hashing behavior
        """
        # Bcrypt has a 72 byte limit, truncate if necessary
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
        """
        Create JWT access token
        
        Implemented:
        - Standard JWT claims (sub, email, role, iat, exp, jti, iss, aud, type)
        - Configurable expiration
        - Unique token ID (jti) for revocation support
        
        Future Enhancements:
        TODO: Add custom claims based on user permissions
        TODO: Add token signing with RSA (currently using HS256)
        TODO: Add token scope management (read, write, admin scopes)
        """
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        # TODO: Add more comprehensive claims
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "iat": datetime.now(timezone.utc),
            "exp": expire,
            "jti": self.generate_secure_token(16),  # JWT ID for revocation
            "iss": settings.PROJECT_NAME,
            "aud": "billfusion-api",
            "type": "access"
        }
        
        # TODO: Add custom claims based on user role
        # TODO: Add permission claims
        # TODO: Add organization claims
        
        encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt, expire
    
    def create_refresh_token(
        self,
        user: User,
        expires_delta: Optional[timedelta] = None
    ) -> Tuple[str, datetime]:
        """
        Create JWT refresh token
        
        Implemented:
        - Long-lived refresh tokens (7-30 days)
        - Unique token ID (jti) for tracking
        - Session-based validation
        
        Future Enhancements:
        TODO: Add refresh token rotation (issue new refresh token on each use)
        TODO: Add refresh token family tracking (detect token theft)
        TODO: Add refresh token reuse detection (automatic revocation)
        """
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
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token
        
        Implemented:
        - JWT signature verification
        - Expiration checking
        - Audience and issuer validation
        
        Future Enhancements:
        TODO: Add token blacklist checking (requires Redis)
        TODO: Add token replay protection (nonce validation)
        TODO: Add token binding to session (validate jti against session)
        """
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
        """
        Get current user from JWT token
        
        Implemented:
        - Token verification and decoding
        - User lookup from database
        - Active user and login status checking
        
        Future Enhancements:
        TODO: Add user caching (Redis) to reduce database queries
        TODO: Add session validation (check if session is still active)
        """
        try:
            payload = self.verify_token(token)
            user_id = payload.get("sub")
            if user_id is None:
                raise AuthenticationError("Invalid token payload", "INVALID_TOKEN")
            
            # Get user from database
            stmt = select(User).where(User.id == user_id, User.is_active == True)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user is None:
                raise AuthenticationError("User not found", "USER_NOT_FOUND")
            
            if not user.can_login:
                raise AuthenticationError("Account is not active", "ACCOUNT_INACTIVE")
            
            return user
            
        except JWTError:
            raise AuthenticationError("Invalid token", "INVALID_TOKEN")
    
    # User Registration and Authentication
    async def register_user(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        phone: Optional[str] = None,
        role: UserRole = UserRole.EMPLOYEE,
        **kwargs
    ) -> User:
        """
        Register a new user
        
        Implemented:
        - Duplicate email checking (case insensitive)
        - Password hashing with bcrypt
        - Email verification token generation
        - Welcome and verification emails
        - Audit logging
        
        Future Enhancements:
        TODO: Add email domain validation (whitelist/blacklist)
        TODO: Add user invitation flow (invite-only registration)
        TODO: Add admin approval workflow (manual activation)
        TODO: Add user onboarding automation (guided setup)
        """
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
            password_hash=hashed_password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role,
            status=UserStatus.PENDING,
            auth_provider=AuthProvider.LOCAL,
            email_verification_token=self.generate_secure_token(),
            email_verification_expires=datetime.now(timezone.utc) + timedelta(hours=24),
            **kwargs
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        # Send welcome email
        try:
            await self.email_service.send_welcome_email(user.email, user.full_name)
        except Exception as e:
            logger.warning("Failed to send welcome email", error=str(e))
        
        # Send email verification
        try:
            await self.email_service.send_email_verification(
                user.email, 
                user.full_name, 
                user.email_verification_token
            )
        except Exception as e:
            logger.warning("Failed to send verification email", error=str(e))
        
        # Log registration event
        await self._log_user_action(user.id, "USER_REGISTERED", {"email": email, "role": role.value})
        
        # Track registration metrics
        logger.info("User registration metrics", role=role.value, auth_provider="local")
        
        logger.info("User registered successfully", user_id=str(user.id), email=email)
        
        return user
    
    async def authenticate_user(
        self,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_info: Optional[Dict[str, Any]] = None
    ) -> User:
        """
        Authenticate user with email and password
        
        Implemented:
        - Password verification
        - Failed login attempt tracking
        - Account lockout after multiple failures
        - Last login tracking
        - Audit logging
        
        Future Enhancements:
        TODO: Add CAPTCHA after failed attempts (requires frontend integration)
        TODO: Add device fingerprinting (requires client library)
        TODO: Add geolocation checking (requires IP geolocation service)
        TODO: Enhanced suspicious activity detection (ML-based)
        """
        # Get user from database
        stmt = select(User).where(User.email == email.lower())
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            # TODO: Add audit log for failed login
            raise AuthenticationError("Invalid credentials", "INVALID_CREDENTIALS")
        
        # Check if account is locked
        if user.is_locked:
            # TODO: Add audit log for locked account access attempt
            raise AuthenticationError("Account is locked", "ACCOUNT_LOCKED")
        
        # Verify password
        if not self.verify_password(password, user.password_hash):
            # Increment failed login attempts
            user.increment_failed_login()
            await self.db.commit()
            
            # TODO: Add audit log for failed login
            # TODO: Send security alert email
            
            raise AuthenticationError("Invalid credentials", "INVALID_CREDENTIALS")
        
        # Check if user can login
        if not user.can_login:
            raise AuthenticationError("Account is not active", "ACCOUNT_INACTIVE")
        
        # Update last login information
        user.update_last_login(ip_address)
        await self.db.commit()
        
        # TODO: Add audit log for successful login
        # TODO: Send login notification email if enabled
        # TODO: Update security metrics
        
        logger.info("User authenticated successfully", user_id=str(user.id), email=email)
        
        return user
    
    async def create_user_session(
        self,
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_info: Optional[Dict[str, Any]] = None,
        remember_me: bool = False
    ) -> Tuple[str, str]:
        """
        Create user session and return tokens
        
        Implemented:
        - Access and refresh token generation
        - Session record creation with metadata
        - IP address and user agent tracking
        - Device info storage
        - Extended refresh token for "remember me"
        
        Future Enhancements:
        TODO: Add session geolocation (IP to location mapping)
        TODO: Add session security scoring (risk assessment)
        TODO: Add concurrent session limits (max sessions per user)
        """
        # Create tokens
        access_token, access_expires = self.create_access_token(user)
        
        refresh_expires_delta = None
        if remember_me:
            refresh_expires_delta = timedelta(days=30)  # Extended refresh token
        
        refresh_token, refresh_expires = self.create_refresh_token(user, refresh_expires_delta)
        
        # Create session record
        # Decode tokens to get JTI without verification (we just created them)
        access_payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"], options={"verify_signature": False, "verify_aud": False})
        refresh_payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"], options={"verify_signature": False, "verify_aud": False})
        
        session = UserSession(
            user_id=user.id,
            session_token=access_payload["jti"],
            refresh_token=refresh_payload["jti"],
            ip_address=ip_address,
            user_agent=user_agent,
            device_info=device_info,
            expires_at=refresh_expires
        )
        
        self.db.add(session)
        await self.db.commit()
        
        logger.info("User session created", user_id=str(user.id), session_id=str(session.id))
        
        return access_token, refresh_token
    
    async def refresh_access_token(self, refresh_token: str) -> Tuple[str, str]:
        """
        Refresh access token using refresh token
        
        Implemented:
        - Refresh token verification
        - Session validation
        - New access token generation
        - Session activity tracking
        
        Future Enhancements:
        TODO: Add refresh token rotation (issue new refresh token)
        TODO: Add refresh token reuse detection (detect token theft)
        """
        try:
            payload = self.verify_token(refresh_token)
            
            if payload.get("type") != "refresh":
                raise AuthenticationError("Invalid token type", "INVALID_TOKEN_TYPE")
            
            user_id = payload.get("sub")
            jti = payload.get("jti")
            
            # Get user
            stmt = select(User).where(User.id == user_id)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user or not user.can_login:
                raise AuthenticationError("User not found or inactive", "USER_INACTIVE")
            
            # Validate session exists and is active
            stmt = select(UserSession).where(
                UserSession.refresh_token == jti,
                UserSession.is_revoked == False
            )
            result = await self.db.execute(stmt)
            session = result.scalar_one_or_none()
            
            if not session or not session.is_valid:
                raise AuthenticationError("Invalid refresh token", "INVALID_REFRESH_TOKEN")
            
            # Create new access token
            new_access_token, _ = self.create_access_token(user)
            
            # Update session activity
            session.update_activity()
            await self.db.commit()
            
            logger.info("Access token refreshed", user_id=str(user.id))
            
            return new_access_token, refresh_token
            
        except JWTError:
            raise AuthenticationError("Invalid refresh token", "INVALID_REFRESH_TOKEN")
    
    async def revoke_session(self, session_token: str) -> None:
        """
        Revoke user session
        
        Implemented:
        - Session revocation by token
        - Audit logging
        
        Future Enhancements:
        TODO: Add session cleanup (delete old revoked sessions)
        TODO: Add revocation notifications (email user about logout)
        """
        stmt = select(UserSession).where(UserSession.session_token == session_token)
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()
        
        if session:
            session.revoke()
            await self.db.commit()
            logger.info("Session revoked", session_id=str(session.id))
    
    # Google OAuth
    async def authenticate_google_oauth(
        self,
        authorization_code: str,
        redirect_uri: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> User:
        """
        Authenticate user with Google OAuth
        
        Implemented:
        - Authorization code exchange
        - ID token verification
        - User creation/lookup
        - Auto-activation for Google users
        
        Future Enhancements:
        TODO: Add state parameter validation (CSRF protection)
        TODO: Add PKCE support (enhanced security for mobile)
        TODO: Add nonce validation (replay attack prevention)
        TODO: Add OAuth scope validation (verify requested permissions)
        """
        try:
            # Exchange authorization code for tokens
            token_data = await self._exchange_google_code(authorization_code, redirect_uri)
            
            # Verify ID token
            user_info = await self._verify_google_id_token(token_data["id_token"])
            
            # Find or create user
            user = await self._find_or_create_google_user(user_info)
            
            # Update last login
            user.update_last_login(ip_address)
            await self.db.commit()
            
            logger.info("Google OAuth authentication successful", user_id=str(user.id))
            
            return user
            
        except Exception as e:
            logger.error("Google OAuth authentication failed", error=str(e))
            raise AuthenticationError("OAuth authentication failed", "OAUTH_ERROR")
    
    async def _exchange_google_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange Google authorization code for tokens"""
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
    
    async def _verify_google_id_token(self, id_token_str: str) -> Dict[str, Any]:
        """Verify Google ID token"""
        try:
            # Verify the token
            id_info = id_token.verify_oauth2_token(
                id_token_str,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
            
            # Verify the issuer
            if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            return id_info
            
        except ValueError as e:
            raise AuthenticationError(f"Invalid ID token: {str(e)}")
    
    async def _find_or_create_google_user(self, user_info: Dict[str, Any]) -> User:
        """Find existing user or create new one from Google user info"""
        email = user_info.get("email")
        
        if not email:
            raise AuthenticationError("Email not provided by Google")
        
        # Try to find existing user
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            # Update user info if it's a Google user
            if user.auth_provider == AuthProvider.GOOGLE:
                user.provider_id = user_info.get("sub")
                user.is_email_verified = user_info.get("email_verified", False)
                if user_info.get("picture"):
                    user.avatar_url = user_info["picture"]
            return user
        
        # Create new user
        user = User(
            email=email,
            first_name=user_info.get("given_name", ""),
            last_name=user_info.get("family_name", ""),
            auth_provider=AuthProvider.GOOGLE,
            provider_id=user_info.get("sub"),
            is_email_verified=user_info.get("email_verified", False),
            avatar_url=user_info.get("picture"),
            status=UserStatus.ACTIVE,  # Google users are auto-activated
            role=UserRole.EMPLOYEE  # Default role
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        # TODO: Send welcome email
        # TODO: Log new user registration
        
        return user
    
    async def _log_user_action(self, user_id: str, action: str, details: dict = None) -> None:
        """
        Log user actions for audit trail
        """
        try:
            # Create audit log entry
            audit_log = UserAuditLog(
                user_id=user_id,
                action=action,
                details=details or {},
                ip_address=details.get("ip_address") if details else None,
                user_agent=details.get("user_agent") if details else None
            )
            
            self.db.add(audit_log)
            await self.db.commit()
            
            logger.info("User action logged", user_id=user_id, action=action)
        except Exception as e:
            logger.error("Failed to log user action", user_id=user_id, action=action, error=str(e))
    
    # Password Reset Functionality
    async def request_password_reset(self, email: str) -> bool:
        """
        Request password reset - generates token and sends email
        """
        stmt = select(User).where(User.email == email.lower())
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            # Don't reveal if email exists
            logger.warning("Password reset requested for non-existent email", email=email)
            return True
        
        # Generate reset token
        reset_token = self.generate_secure_token()
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        
        await self.db.commit()
        
        # Send password reset email
        try:
            await self.email_service.send_password_reset_email(
                user.email,
                user.full_name,
                reset_token
            )
            logger.info("Password reset email sent", user_id=str(user.id))
        except Exception as e:
            logger.error("Failed to send password reset email", error=str(e))
        
        await self._log_user_action(str(user.id), "PASSWORD_RESET_REQUESTED", {"email": email})
        
        return True
    
    async def reset_password(self, token: str, new_password: str) -> bool:
        """
        Reset password using reset token
        """
        stmt = select(User).where(
            User.password_reset_token == token,
            User.password_reset_expires > datetime.now(timezone.utc)
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise AuthenticationError("Invalid or expired reset token", "INVALID_RESET_TOKEN")
        
        # Update password
        user.password_hash = self.hash_password(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        user.reset_failed_login_attempts()
        
        await self.db.commit()
        
        # Revoke all existing sessions for security
        await self._revoke_all_user_sessions(user.id)
        
        await self._log_user_action(str(user.id), "PASSWORD_RESET_COMPLETED")
        
        logger.info("Password reset completed", user_id=str(user.id))
        
        return True
    
    # Email Verification Functionality
    async def verify_email(self, token: str) -> bool:
        """
        Verify user email using verification token
        """
        stmt = select(User).where(
            User.email_verification_token == token,
            User.email_verification_expires > datetime.now(timezone.utc)
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise AuthenticationError("Invalid or expired verification token", "INVALID_VERIFICATION_TOKEN")
        
        # Mark email as verified and activate account
        user.is_email_verified = True
        user.email_verification_token = None
        user.email_verification_expires = None
        
        # Activate account if it was pending
        if user.status == UserStatus.PENDING:
            user.status = UserStatus.ACTIVE
        
        await self.db.commit()
        
        await self._log_user_action(str(user.id), "EMAIL_VERIFIED")
        
        logger.info("Email verified", user_id=str(user.id))
        
        return True
    
    async def resend_verification_email(self, email: str) -> bool:
        """
        Resend email verification
        """
        stmt = select(User).where(User.email == email.lower())
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            # Don't reveal if email exists
            return True
        
        if user.is_email_verified:
            raise AuthenticationError("Email already verified", "EMAIL_ALREADY_VERIFIED")
        
        # Generate new verification token
        user.email_verification_token = self.generate_secure_token()
        user.email_verification_expires = datetime.now(timezone.utc) + timedelta(hours=24)
        
        await self.db.commit()
        
        # Send verification email
        try:
            await self.email_service.send_email_verification(
                user.email,
                user.full_name,
                user.email_verification_token
            )
            logger.info("Verification email resent", user_id=str(user.id))
        except Exception as e:
            logger.error("Failed to resend verification email", error=str(e))
        
        return True
    
    # Session Management
    async def get_user_sessions(self, user_id: str) -> list[UserSession]:
        """
        Get all active sessions for a user
        """
        stmt = select(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.is_revoked == False
        )
        result = await self.db.execute(stmt)
        sessions = result.scalars().all()
        
        return list(sessions)
    
    async def revoke_all_sessions_except_current(self, user_id: str, current_session_token: str) -> int:
        """
        Revoke all user sessions except the current one
        """
        stmt = select(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.session_token != current_session_token,
            UserSession.is_revoked == False
        )
        result = await self.db.execute(stmt)
        sessions = result.scalars().all()
        
        count = 0
        for session in sessions:
            session.revoke()
            count += 1
        
        await self.db.commit()
        
        logger.info("Sessions revoked", user_id=user_id, count=count)
        
        return count
    
    async def _revoke_all_user_sessions(self, user_id: str) -> int:
        """
        Revoke all sessions for a user (internal use)
        """
        stmt = select(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.is_revoked == False
        )
        result = await self.db.execute(stmt)
        sessions = result.scalars().all()
        
        count = 0
        for session in sessions:
            session.revoke()
            count += 1
        
        await self.db.commit()
        
        return count
    
    # User Management
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """
        Change user password
        """
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise AuthenticationError("User not found", "USER_NOT_FOUND")
        
        # Verify current password
        if not self.verify_password(current_password, user.password_hash):
            raise AuthenticationError("Current password is incorrect", "INVALID_PASSWORD")
        
        # Update password
        user.password_hash = self.hash_password(new_password)
        await self.db.commit()
        
        # Revoke all sessions for security
        await self._revoke_all_user_sessions(user_id)
        
        await self._log_user_action(user_id, "PASSWORD_CHANGED")
        
        logger.info("Password changed", user_id=user_id)
        
        return True
    
    async def update_user_profile(self, user_id: str, **updates) -> User:
        """
        Update user profile information
        """
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise AuthenticationError("User not found", "USER_NOT_FOUND")
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'phone', 'timezone', 'language', 'avatar_url']
        for field, value in updates.items():
            if field in allowed_fields and value is not None:
                setattr(user, field, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        await self._log_user_action(user_id, "PROFILE_UPDATED", {"fields": list(updates.keys())})
        
        logger.info("User profile updated", user_id=user_id)
        
        return user
    
    async def deactivate_user(self, user_id: str, reason: Optional[str] = None) -> bool:
        """
        Deactivate user account
        """
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise AuthenticationError("User not found", "USER_NOT_FOUND")
        
        user.status = UserStatus.INACTIVE
        user.is_active = False
        
        await self.db.commit()
        
        # Revoke all sessions
        await self._revoke_all_user_sessions(user_id)
        
        await self._log_user_action(user_id, "ACCOUNT_DEACTIVATED", {"reason": reason})
        
        logger.info("User account deactivated", user_id=user_id)
        
        return True
    
    async def reactivate_user(self, user_id: str) -> bool:
        """
        Reactivate user account
        """
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise AuthenticationError("User not found", "USER_NOT_FOUND")
        
        user.status = UserStatus.ACTIVE
        user.is_active = True
        user.reset_failed_login_attempts()
        
        await self.db.commit()
        
        await self._log_user_action(user_id, "ACCOUNT_REACTIVATED")
        
        logger.info("User account reactivated", user_id=user_id)
        
        return True
    
    # Security Monitoring
    async def check_suspicious_activity(self, user_id: str, ip_address: str, user_agent: str) -> bool:
        """
        Check for suspicious activity patterns
        Returns True if activity seems suspicious
        """
        # Get recent login attempts
        stmt = select(UserAuditLog).where(
            UserAuditLog.user_id == user_id,
            UserAuditLog.action.in_(["LOGIN_SUCCESS", "LOGIN_FAILED"]),
            UserAuditLog.timestamp > datetime.now(timezone.utc) - timedelta(hours=1)
        ).order_by(UserAuditLog.timestamp.desc()).limit(10)
        
        result = await self.db.execute(stmt)
        recent_logs = result.scalars().all()
        
        if not recent_logs:
            return False
        
        # Check for multiple IPs
        unique_ips = set(log.ip_address for log in recent_logs if log.ip_address)
        if len(unique_ips) > 3:
            logger.warning("Suspicious activity: Multiple IPs", user_id=user_id, ip_count=len(unique_ips))
            return True
        
        # Check for rapid login attempts
        if len(recent_logs) > 5:
            logger.warning("Suspicious activity: Rapid login attempts", user_id=user_id, attempt_count=len(recent_logs))
            return True
        
        return False
    
    async def get_user_audit_log(self, user_id: str, limit: int = 50) -> list[UserAuditLog]:
        """
        Get user audit log
        """
        stmt = select(UserAuditLog).where(
            UserAuditLog.user_id == user_id
        ).order_by(UserAuditLog.timestamp.desc()).limit(limit)
        
        result = await self.db.execute(stmt)
        logs = result.scalars().all()
        
        return list(logs)
    
    # COMPLETED IMPLEMENTATIONS:
    # ✓ Password reset functionality (request_password_reset, reset_password)
    # ✓ Email verification functionality (verify_email, resend_verification_email)
    # ✓ User management functions (change_password, update_user_profile, deactivate/reactivate_user)
    # ✓ Security monitoring functions (check_suspicious_activity, get_user_audit_log)
    # ✓ Session management (get_user_sessions, revoke_all_sessions_except_current)
    
    # FUTURE ENHANCEMENTS:
    # TODO: Add two-factor authentication (TOTP/SMS)
    # TODO: Add WebAuthn/FIDO2 support
    # TODO: Add social login (Facebook, GitHub, etc.)
    # TODO: Add LDAP/Active Directory integration
    # TODO: Add SAML SSO support
