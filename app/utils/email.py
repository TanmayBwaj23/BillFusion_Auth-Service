"""
Email service utilities for sending notifications
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from pathlib import Path
import aiosmtplib
import structlog

from app.core.config import settings

# TODO: Add email templates
# TODO: Add email queuing
# TODO: Add email delivery tracking
# TODO: Add email bounce handling
# TODO: Add email analytics
# TODO: Add email personalization
# TODO: Add email A/B testing
# TODO: Add email scheduling
# TODO: Add email attachments
# TODO: Add email encryption

logger = structlog.get_logger()


class EmailService:
    """
    Email service for sending notifications and communications
    
    TODO: Add multiple email providers support
    TODO: Add email failover
    TODO: Add email delivery optimization
    TODO: Add email compliance features
    """
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_use_tls = settings.SMTP_USE_TLS
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        Send email using SMTP
        
        TODO: Add email validation
        TODO: Add delivery confirmation
        TODO: Add retry logic
        TODO: Add email tracking
        """
        try:
            if not self.smtp_host or not self.smtp_username:
                logger.warning("SMTP not configured, skipping email")
                return False
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{from_name or 'BillFusion'} <{from_email or self.smtp_username}>"
            message["To"] = to_email
            
            # Add text and HTML parts
            text_part = MIMEText(body, "plain")
            message.attach(text_part)
            
            if html_body:
                html_part = MIMEText(html_body, "html")
                message.attach(html_part)
            
            # Add attachments if any
            if attachments:
                for file_path in attachments:
                    with open(file_path, "rb") as attachment:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())
                    
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {Path(file_path).name}",
                    )
                    message.attach(part)
            
            # Send email using async SMTP
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                use_tls=self.smtp_use_tls,
            )
            
            logger.info(
                "Email sent successfully",
                to_email=to_email,
                subject=subject
            )
            return True
            
        except Exception as e:
            logger.error(
                "Failed to send email",
                to_email=to_email,
                subject=subject,
                error=str(e)
            )
            return False
    
    async def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Send welcome email to new users"""
        subject = "Welcome to BillFusion!"
        body = f"""
        Hi {user_name},
        
        Welcome to BillFusion! Your account has been created successfully.
        
        You can now access your dashboard and start managing your billing and reports.
        
        If you have any questions, please don't hesitate to contact our support team.
        
        Best regards,
        The BillFusion Team
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Welcome to BillFusion!</h2>
            <p>Hi {user_name},</p>
            <p>Welcome to BillFusion! Your account has been created successfully.</p>
            <p>You can now access your dashboard and start managing your billing and reports.</p>
            <p>If you have any questions, please don't hesitate to contact our support team.</p>
            <br>
            <p>Best regards,<br>The BillFusion Team</p>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=user_email,
            subject=subject,
            body=body,
            html_body=html_body
        )
    
    async def send_verification_email(self, user_email: str, user_name: str, verification_token: str) -> bool:
        """Send email verification email"""
        verification_url = f"http://localhost:3000/verify-email?token={verification_token}"
        
        subject = "Verify Your Email Address"
        body = f"""
        Hi {user_name},
        
        Please verify your email address by clicking the link below:
        
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you didn't create an account with BillFusion, please ignore this email.
        
        Best regards,
        The BillFusion Team
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Verify Your Email Address</h2>
            <p>Hi {user_name},</p>
            <p>Please verify your email address by clicking the button below:</p>
            <p style="text-align: center;">
                <a href="{verification_url}" 
                   style="background-color: #4CAF50; color: white; padding: 14px 20px; 
                          text-decoration: none; border-radius: 4px; display: inline-block;">
                    Verify Email
                </a>
            </p>
            <p>Or copy and paste this link in your browser:</p>
            <p><a href="{verification_url}">{verification_url}</a></p>
            <p><small>This link will expire in 24 hours.</small></p>
            <p>If you didn't create an account with BillFusion, please ignore this email.</p>
            <br>
            <p>Best regards,<br>The BillFusion Team</p>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=user_email,
            subject=subject,
            body=body,
            html_body=html_body
        )
    
    async def send_password_reset_email(self, user_email: str, user_name: str, reset_token: str) -> bool:
        """Send password reset email"""
        reset_url = f"http://localhost:3000/reset-password?token={reset_token}"
        
        subject = "Reset Your Password"
        body = f"""
        Hi {user_name},
        
        You requested to reset your password. Click the link below to reset it:
        
        {reset_url}
        
        This link will expire in 1 hour.
        
        If you didn't request a password reset, please ignore this email.
        
        Best regards,
        The BillFusion Team
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Reset Your Password</h2>
            <p>Hi {user_name},</p>
            <p>You requested to reset your password. Click the button below to reset it:</p>
            <p style="text-align: center;">
                <a href="{reset_url}" 
                   style="background-color: #f44336; color: white; padding: 14px 20px; 
                          text-decoration: none; border-radius: 4px; display: inline-block;">
                    Reset Password
                </a>
            </p>
            <p>Or copy and paste this link in your browser:</p>
            <p><a href="{reset_url}">{reset_url}</a></p>
            <p><small>This link will expire in 1 hour.</small></p>
            <p>If you didn't request a password reset, please ignore this email.</p>
            <br>
            <p>Best regards,<br>The BillFusion Team</p>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=user_email,
            subject=subject,
            body=body,
            html_body=html_body
        )
    
    async def send_login_notification(
        self, 
        user_email: str, 
        user_name: str, 
        ip_address: str, 
        user_agent: str,
        login_time: str
    ) -> bool:
        """Send login notification email"""
        subject = "New Login to Your Account"
        body = f"""
        Hi {user_name},
        
        We detected a new login to your BillFusion account:
        
        Time: {login_time}
        IP Address: {ip_address}
        Device: {user_agent}
        
        If this wasn't you, please secure your account immediately by changing your password.
        
        Best regards,
        The BillFusion Team
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>New Login to Your Account</h2>
            <p>Hi {user_name},</p>
            <p>We detected a new login to your BillFusion account:</p>
            <ul>
                <li><strong>Time:</strong> {login_time}</li>
                <li><strong>IP Address:</strong> {ip_address}</li>
                <li><strong>Device:</strong> {user_agent}</li>
            </ul>
            <p>If this wasn't you, please secure your account immediately by changing your password.</p>
            <br>
            <p>Best regards,<br>The BillFusion Team</p>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=user_email,
            subject=subject,
            body=body,
            html_body=html_body
        )
    
    async def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """
        Send welcome email to new users
        """
        subject = "Welcome to BillFusion!"
        body = f"""Hello {user_name},

Welcome to BillFusion! Your account has been successfully created.

You can now log in and start using our unified billing and reporting platform.

Best regards,
The BillFusion Team"""
        
        html_body = f"""<!DOCTYPE html>
<html>
<head>
    <title>Welcome to BillFusion</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #f8f9fa; padding: 30px; border-radius: 8px;">
        <h1 style="color: #2563eb; text-align: center;">Welcome to BillFusion!</h1>
        
        <p>Hello {user_name},</p>
        
        <p>Welcome to BillFusion! Your account has been successfully created.</p>
        
        <div style="background-color: #e3f2fd; padding: 20px; border-radius: 6px; margin: 20px 0;">
            <p><strong>What's next?</strong></p>
            <ul>
                <li>Complete your profile setup</li>
                <li>Explore the dashboard</li>
                <li>Set up your billing preferences</li>
            </ul>
        </div>
        
        <p>You can now log in and start using our unified billing and reporting platform.</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{settings.FRONTEND_URL}/login" style="background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Login Now</a>
        </div>
        
        <p>Best regards,<br>The BillFusion Team</p>
    </div>
</body>
</html>"""
        
        return await self.send_email(
            to_email=user_email,
            subject=subject,
            body=body,
            html_body=html_body
        )
    
    async def send_email_verification(self, user_email: str, user_name: str, verification_token: str) -> bool:
        """
        Send email verification link
        """
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
        
        subject = "Verify your BillFusion email address"
        body = f"""Hello {user_name},

Please verify your email address by clicking the link below:

{verification_url}

This link will expire in 24 hours.

If you did not create this account, please ignore this email.

Best regards,
The BillFusion Team"""
        
        html_body = f"""<!DOCTYPE html>
<html>
<head>
    <title>Verify Your Email</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #f8f9fa; padding: 30px; border-radius: 8px;">
        <h1 style="color: #2563eb; text-align: center;">Verify Your Email</h1>
        
        <p>Hello {user_name},</p>
        
        <p>Please verify your email address to complete your account setup.</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{verification_url}" style="background-color: #16a34a; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Verify Email Address</a>
        </div>
        
        <p><small>This link will expire in 24 hours.</small></p>
        
        <p>If you did not create this account, please ignore this email.</p>
        
        <p>Best regards,<br>The BillFusion Team</p>
    </div>
</body>
</html>"""
        
        return await self.send_email(
            to_email=user_email,
            subject=subject,
            body=body,
            html_body=html_body
        )
    
    async def send_password_reset_email(self, user_email: str, user_name: str, reset_token: str) -> bool:
        """
        Send password reset email
        """
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        subject = "Reset your BillFusion password"
        body = f"""Hello {user_name},

We received a request to reset your password. Click the link below to set a new password:

{reset_url}

This link will expire in 1 hour.

If you did not request this password reset, please ignore this email.

Best regards,
The BillFusion Team"""
        
        html_body = f"""<!DOCTYPE html>
<html>
<head>
    <title>Reset Your Password</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #f8f9fa; padding: 30px; border-radius: 8px;">
        <h1 style="color: #2563eb; text-align: center;">Reset Your Password</h1>
        
        <p>Hello {user_name},</p>
        
        <p>We received a request to reset your password.</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_url}" style="background-color: #dc2626; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Reset Password</a>
        </div>
        
        <p><small>This link will expire in 1 hour.</small></p>
        
        <p>If you did not request this password reset, please ignore this email and your password will remain unchanged.</p>
        
        <p>Best regards,<br>The BillFusion Team</p>
    </div>
</body>
</html>"""
        
        return await self.send_email(
            to_email=user_email,
            subject=subject,
            body=body,
            html_body=html_body
        )
