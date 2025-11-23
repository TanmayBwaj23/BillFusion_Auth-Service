"""
Simplified Authentication Pydantic schemas
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
import re


# Base Schemas
class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Authentication Request Schemas
class UserRegistrationRequest(BaseModel):
    """User registration request - simplified"""
    name: str = Field(..., min_length=1, max_length=255, description="Full name")
    email: EmailStr = Field(..., description="User email address")
    phone: str = Field(..., max_length=20, description="Phone number")
    password: str = Field(..., min_length=6, max_length=72, description="User password")
    role: str = Field(default="employee", description="User role (client, vendor, employee)")
    
    @validator('role')
    def validate_role(cls, v):
        """Validate user role"""
        allowed_roles = ["client", "vendor", "employee"]
        if v.lower() not in allowed_roles:
            raise ValueError(f"Role must be one of: {', '.join(allowed_roles)}")
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password"""
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
        """Validate phone number format"""
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
                "role": "employee"
            }
        }


class UserLoginRequest(BaseModel):
    """User login request"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "Pass123!"
            }
        }


# Authentication Response Schemas
class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class UserResponse(BaseModel):
    """User information response"""
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    name: str = Field(..., description="Full name")
    phone: Optional[str] = Field(None, description="Phone number")
    role: str = Field(..., description="User role")
    is_social_login: bool = Field(..., description="Social login status")
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
                "name": "John Doe",
                "phone": "+1234567890",
                "role": "employee",
                "is_social_login": False,
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
    message: str = "Registration successful"
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Registration successful",
                "timestamp": "2023-01-01T12:00:00Z",
                "user": UserResponse.Config.schema_extra["example"]
            }
        }
