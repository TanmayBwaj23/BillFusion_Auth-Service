"""
Password reset functionality for the auth service
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import secrets
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.user import User, UserStatus
from app.utils.email import EmailService
from app.services.auth_service import AuthService

logger = structlog.get_logger()


class PasswordResetService:
    """
    Service for handling password reset functionality
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.email_service = EmailService()
        self.auth_service = AuthService(db_session)
    
    async def request_password_reset(self, email: str) -> bool:
        """
        Request password reset for a user
        """
        # Find user by email
        stmt = select(User).where(User.email == email.lower())
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            # For security, don't reveal if email exists
            logger.info("Password reset requested for non-existent email", email=email)
            return True
        
        if user.status != UserStatus.ACTIVE:
            logger.warning("Password reset requested for inactive user", user_id=str(user.id))
            return False
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        
        # Update user with reset token
        stmt = update(User).where(User.id == user.id).values(
            password_reset_token=reset_token,
            password_reset_expires=reset_expires
        )
        await self.db.execute(stmt)
        await self.db.commit()
        
        # Send password reset email
        try:
            await self.email_service.send_password_reset_email(
                user.email,
                user.full_name,
                reset_token
            )
            logger.info("Password reset email sent", user_id=str(user.id))
            return True
        except Exception as e:
            logger.error("Failed to send password reset email", user_id=str(user.id), error=str(e))
            return False
    
    async def reset_password(self, token: str, new_password: str) -> bool:
        """
        Reset password using reset token
        """
        # Find user by reset token
        stmt = select(User).where(
            User.password_reset_token == token,
            User.password_reset_expires > datetime.now(timezone.utc)
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning("Invalid or expired password reset token", token=token[:8] + "...")
            return False
        
        # Update password and clear reset token
        hashed_password = self.auth_service.hash_password(new_password)
        stmt = update(User).where(User.id == user.id).values(
            password_hash=hashed_password,
            password_reset_token=None,
            password_reset_expires=None,
            failed_login_attempts=0,  # Reset failed attempts
            last_password_change=datetime.now(timezone.utc)
        )
        await self.db.execute(stmt)
        await self.db.commit()
        
        logger.info("Password reset successful", user_id=str(user.id))
        return True
    
    async def verify_email(self, token: str) -> bool:
        """
        Verify user email using verification token
        """
        # Find user by verification token
        stmt = select(User).where(
            User.email_verification_token == token,
            User.email_verification_expires > datetime.now(timezone.utc)
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning("Invalid or expired email verification token", token=token[:8] + "...")
            return False
        
        # Update user as verified and active
        stmt = update(User).where(User.id == user.id).values(
            email_verified=True,
            email_verification_token=None,
            email_verification_expires=None,
            status=UserStatus.ACTIVE,
            email_verified_at=datetime.now(timezone.utc)
        )
        await self.db.execute(stmt)
        await self.db.commit()
        
        logger.info("Email verification successful", user_id=str(user.id))
        return True
    
    async def resend_verification_email(self, email: str) -> bool:
        """
        Resend email verification for a user
        """
        # Find user by email
        stmt = select(User).where(User.email == email.lower())
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return False
        
        if user.email_verified:
            logger.info("Email verification requested for already verified user", user_id=str(user.id))
            return True
        
        # Generate new verification token
        verification_token = secrets.token_urlsafe(32)
        verification_expires = datetime.now(timezone.utc) + timedelta(hours=24)
        
        # Update user with new verification token
        stmt = update(User).where(User.id == user.id).values(
            email_verification_token=verification_token,
            email_verification_expires=verification_expires
        )
        await self.db.execute(stmt)
        await self.db.commit()
        
        # Send verification email
        try:
            await self.email_service.send_email_verification(
                user.email,
                user.full_name,
                verification_token
            )
            logger.info("Verification email resent", user_id=str(user.id))
            return True
        except Exception as e:
            logger.error("Failed to resend verification email", user_id=str(user.id), error=str(e))
            return False
