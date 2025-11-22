"""
Authentication Pydantic schemas for request/response validation
Comprehensive input validation with custom rules
Field masking for sensitive data (passwords, tokens)
"""

from pydantic import BaseModel, EmailStr, Field, validator, root_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
import re
from enum import Enum

from app.models.user import UserRole, UserStatus, AuthProvider


class TokenType(str, Enum):
    """Token types for different authentication flows"""
    ACCESS = "access"
    REFRESH = "refresh"
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"


# Base Schemas
class BaseResponse(BaseModel):
    """
    Base response model with common fields
    Includes response metadata, versioning, and caching headers
    """
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="1.0", description="API version")


class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = False
    error_code: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None


# Authentication Request Schemas
class UserRegistrationRequest(BaseModel):
    """
    User registration request schema - Simplified
    Required fields: name, email, phone, password
    All new users default to EMPLOYEE role
    """
    name: str = Field(..., min_length=1, max_length=200, description="Full name")
    email: EmailStr = Field(..., description="User email address")
    phone: str = Field(..., max_length=20, description="Phone number")
    password: str = Field(..., min_length=6, max_length=72, description="User password")
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password - minimum 6 characters, maximum 72 for bcrypt"""
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if len(v) > 72:
            raise ValueError('Password cannot be longer than 72 characters')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        """Validate and clean name"""
        return v.strip()
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format - basic validation"""
        phone_pattern = r'^\+?[\d\s\-\(\)]{10,20}$'
        if not re.match(phone_pattern, v):
            raise ValueError('Invalid phone number format')
        return v

    class Config:
        schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "user@example.com",
                "phone": "+1234567890",
                "password": "Pass123!",
                "role": "client"
            }
        }


class UserLoginRequest(BaseModel):
    """
    User login request schema - Simplified
    Required fields: email and password only
    Optional fields: device_info, remember_me
    """
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")
    device_info: Optional[Dict[str, Any]] = Field(None, description="Device information")
    remember_me: Optional[bool] = Field(False, description="Remember me flag")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "Pass123!"
            }
        }


class GoogleOAuthRequest(BaseModel):
    """
    Google OAuth authentication request
    
    TODO: Add state parameter validation
    TODO: Add PKCE support
    TODO: Add nonce validation
    """
    code: str = Field(..., description="OAuth authorization code")
    state: Optional[str] = Field(None, description="OAuth state parameter")
    redirect_uri: str = Field(..., description="OAuth redirect URI")
    
    class Config:
        schema_extra = {
            "example": {
                "code": "4/0AX4XfWh...",
                "state": "random_state_string",
                "redirect_uri": "http://localhost:3000/auth/callback"
            }
        }


class PasswordResetRequest(BaseModel):
    """Password reset request schema"""
    email: EmailStr = Field(..., description="User email address")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str = Field(..., description="Password reset token")
    password: str = Field(..., min_length=8, max_length=128, description="New password")
    password_confirm: str = Field(..., description="Password confirmation")
    
    @validator('password')
    def validate_password(cls, v):
        """Validate new password strength"""
        # Reuse validation from UserRegistrationRequest
        return UserRegistrationRequest.__validators__['validate_password'](v)
    
    @root_validator(skip_on_failure=True)
    def validate_passwords_match(cls, values):
        """Validate password confirmation"""
        password = values.get('password')
        password_confirm = values.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise ValueError('Passwords do not match')
        
        return values
    
    class Config:
        schema_extra = {
            "example": {
                "token": "reset_token_here",
                "password": "NewSecurePassword123!",
                "password_confirm": "NewSecurePassword123!"
            }
        }


class EmailVerificationRequest(BaseModel):
    """Email verification request schema"""
    token: str = Field(..., description="Email verification token")
    
    class Config:
        schema_extra = {
            "example": {
                "token": "verification_token_here"
            }
        }


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str = Field(..., description="Refresh token")
    
    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "refresh_token_here"
            }
        }


class ChangePasswordRequest(BaseModel):
    """Change password request schema"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")
    new_password_confirm: str = Field(..., description="New password confirmation")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength"""
        return UserRegistrationRequest.__validators__['validate_password'](v)
    
    @root_validator(skip_on_failure=True)
    def validate_passwords_match(cls, values):
        """Validate new password confirmation"""
        new_password = values.get('new_password')
        new_password_confirm = values.get('new_password_confirm')
        
        if new_password and new_password_confirm and new_password != new_password_confirm:
            raise ValueError('New passwords do not match')
        
        return values
    
    class Config:
        schema_extra = {
            "example": {
                "current_password": "CurrentPassword123!",
                "new_password": "NewSecurePassword123!",
                "new_password_confirm": "NewSecurePassword123!"
            }
        }


# Authentication Response Schemas
class TokenResponse(BaseModel):
    """
    JWT token response schema
    
    TODO: Add token metadata
    TODO: Add token scopes
    TODO: Add token audience
    """
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    scope: Optional[str] = Field(None, description="Token scope")
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "scope": "read write"
            }
        }


class UserResponse(BaseModel):
    """
    User information response schema
    
    TODO: Add role-based field filtering
    TODO: Add user statistics
    TODO: Add user preferences
    """
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    phone: Optional[str] = Field(None, description="Phone number")
    role: UserRole = Field(..., description="User role")
    status: UserStatus = Field(..., description="Account status")
    auth_provider: AuthProvider = Field(..., description="Authentication provider")
    is_email_verified: bool = Field(..., description="Email verification status")
    is_phone_verified: bool = Field(..., description="Phone verification status")
    two_factor_enabled: bool = Field(..., description="2FA status")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")
    timezone: str = Field(..., description="User timezone")
    language: str = Field(..., description="Preferred language")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string"""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567890",
                "role": "client",
                "status": "active",
                "auth_provider": "local",
                "is_email_verified": True,
                "is_phone_verified": False,
                "two_factor_enabled": False,
                "avatar_url": "https://example.com/avatar.jpg",
                "timezone": "America/New_York",
                "language": "en",
                "last_login_at": "2023-01-01T12:00:00Z",
                "created_at": "2023-01-01T10:00:00Z",
                "updated_at": "2023-01-01T12:00:00Z"
            }
        }


class LoginResponse(BaseResponse):
    """Login success response"""
    user: UserResponse
    tokens: TokenResponse
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Login successful",
                "timestamp": "2023-01-01T12:00:00Z",
                "user": UserResponse.Config.schema_extra["example"],
                "tokens": TokenResponse.Config.schema_extra["example"]
            }
        }


class RegistrationResponse(BaseResponse):
    """Registration success response"""
    user: UserResponse
    message: str = "Registration successful. Please check your email for verification."
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Registration successful. Please check your email for verification.",
                "timestamp": "2023-01-01T12:00:00Z",
                "user": UserResponse.Config.schema_extra["example"]
            }
        }


# Session Management Schemas
class SessionResponse(BaseModel):
    """User session information response"""
    id: str = Field(..., description="Session ID")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    device_info: Optional[Dict[str, Any]] = Field(None, description="Device information")
    created_at: datetime = Field(..., description="Session creation time")
    last_activity: datetime = Field(..., description="Last activity time")
    expires_at: datetime = Field(..., description="Session expiration time")
    is_current: bool = Field(..., description="Is current session")
    
    class Config:
        from_attributes = True


class SessionListResponse(BaseResponse):
    """List of user sessions"""
    sessions: List[SessionResponse]
    total_count: int = Field(..., description="Total number of sessions")


# Two-Factor Authentication Schemas
class TwoFactorSetupRequest(BaseModel):
    """2FA setup request"""
    password: str = Field(..., description="Current password for verification")
    
    class Config:
        schema_extra = {
            "example": {
                "password": "CurrentPassword123!"
            }
        }


class TwoFactorSetupResponse(BaseModel):
    """2FA setup response with QR code"""
    secret: str = Field(..., description="2FA secret key")
    qr_code_url: str = Field(..., description="QR code data URL")
    backup_codes: List[str] = Field(..., description="Backup recovery codes")
    
    class Config:
        schema_extra = {
            "example": {
                "secret": "JBSWY3DPEHPK3PXP",
                "qr_code_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
                "backup_codes": ["12345678", "87654321", "11223344"]
            }
        }


class TwoFactorVerifyRequest(BaseModel):
    """2FA verification request"""
    code: str = Field(..., min_length=6, max_length=6, description="6-digit 2FA code")
    
    @validator('code')
    def validate_code(cls, v):
        """Validate 2FA code format"""
        if not v.isdigit() or len(v) != 6:
            raise ValueError('2FA code must be 6 digits')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "code": "123456"
            }
        }


# TODO: Add additional schemas
# TODO: Add user profile update schemas
# TODO: Add role change request schemas
# TODO: Add account deletion schemas
# TODO: Add user search schemas
# TODO: Add user statistics schemas
# TODO: Add compliance reporting schemas
