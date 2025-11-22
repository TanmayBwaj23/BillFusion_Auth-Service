"""
Enhanced Application Configuration with all TODO tasks completed
Handles all environment variables, application settings, and comprehensive validation
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator, root_validator
from typing import List, Optional, Dict, Any, Union
import secrets
import logging
from pathlib import Path
import re
from urllib.parse import urlparse


class DatabaseConfig(BaseSettings):
    """Database configuration with validation"""
    url: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/billfusion_auth",
        description="Database connection URL"
    )
    pool_size: int = Field(default=10, description="Connection pool size")
    max_overflow: int = Field(default=20, description="Max overflow connections")
    pool_timeout: int = Field(default=30, description="Pool checkout timeout")
    pool_recycle: int = Field(default=3600, description="Connection recycle time")
    echo: bool = Field(default=False, description="Echo SQL queries")
    
    # Migration settings
    migration_timeout: int = Field(default=300, description="Migration timeout in seconds")
    auto_migrate: bool = Field(default=False, description="Auto-run migrations on startup")
    
    # Backup configuration
    backup_enabled: bool = Field(default=True, description="Enable automatic backups")
    backup_schedule: str = Field(default="0 2 * * *", description="Backup cron schedule")
    backup_retention_days: int = Field(default=30, description="Backup retention period")

    @validator("url")
    def validate_url(cls, v):
        if not v or not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("DATABASE_URL must be a valid PostgreSQL URL")
        
        # Parse and validate URL components
        try:
            parsed = urlparse(v)
            if not parsed.hostname or not parsed.port:
                raise ValueError("Database URL must include hostname and port")
        except Exception as e:
            raise ValueError(f"Invalid database URL: {e}")
        
        return v


class RedisConfig(BaseSettings):
    """Redis configuration with cluster support"""
    url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    password: Optional[str] = Field(default=None, description="Redis password")
    ssl_enabled: bool = Field(default=False, description="Enable SSL/TLS")
    ssl_cert_path: Optional[str] = Field(default=None, description="SSL certificate path")
    
    # Cluster configuration
    cluster_enabled: bool = Field(default=False, description="Enable Redis cluster")
    cluster_nodes: List[str] = Field(default=[], description="Redis cluster nodes")
    
    # Connection settings
    max_connections: int = Field(default=20, description="Maximum connections")
    retry_on_timeout: bool = Field(default=True, description="Retry on timeout")
    socket_timeout: int = Field(default=5, description="Socket timeout")


class OAuthConfig(BaseSettings):
    """OAuth providers configuration"""
    # Google OAuth
    google_client_id: Optional[str] = Field(default=None, description="Google OAuth client ID")
    google_client_secret: Optional[str] = Field(default=None, description="Google OAuth client secret")
    google_redirect_uri: str = Field(
        default="http://localhost:8000/api/v1/auth/google/callback",
        description="Google OAuth redirect URI"
    )
    google_scopes: List[str] = Field(
        default=["openid", "email", "profile"],
        description="Google OAuth scopes"
    )
    
    # Microsoft OAuth
    microsoft_client_id: Optional[str] = Field(default=None, description="Microsoft OAuth client ID")
    microsoft_client_secret: Optional[str] = Field(default=None, description="Microsoft OAuth client secret")
    microsoft_tenant_id: Optional[str] = Field(default="common", description="Microsoft tenant ID")
    
    # Apple OAuth
    apple_client_id: Optional[str] = Field(default=None, description="Apple OAuth client ID")
    apple_team_id: Optional[str] = Field(default=None, description="Apple team ID")
    apple_key_id: Optional[str] = Field(default=None, description="Apple key ID")
    apple_private_key: Optional[str] = Field(default=None, description="Apple private key")
    
    # GitHub OAuth
    github_client_id: Optional[str] = Field(default=None, description="GitHub OAuth client ID")
    github_client_secret: Optional[str] = Field(default=None, description="GitHub OAuth client secret")

    @validator("google_client_id", "microsoft_client_id", "apple_client_id", "github_client_id")
    def validate_oauth_client_id(cls, v, field):
        if v and len(v) < 10:
            raise ValueError(f"{field.name} must be at least 10 characters long")
        return v


class SecurityConfig(BaseSettings):
    """Enhanced security configuration"""
    secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    access_token_expire_minutes: int = Field(default=30, description="JWT access token expiration")
    refresh_token_expire_days: int = Field(default=7, description="JWT refresh token expiration")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    
    # Password policy
    password_min_length: int = Field(default=8, description="Minimum password length")
    password_require_uppercase: bool = Field(default=True, description="Require uppercase letters")
    password_require_lowercase: bool = Field(default=True, description="Require lowercase letters")
    password_require_numbers: bool = Field(default=True, description="Require numbers")
    password_require_special_chars: bool = Field(default=True, description="Require special characters")
    password_max_age_days: int = Field(default=90, description="Password expiration in days")
    password_history_count: int = Field(default=5, description="Remember last N passwords")
    
    # Account lockout
    max_failed_login_attempts: int = Field(default=5, description="Max failed login attempts")
    account_lockout_duration_minutes: int = Field(default=15, description="Account lockout duration")
    
    # Session management
    session_timeout_minutes: int = Field(default=30, description="Session timeout")
    concurrent_sessions_limit: int = Field(default=3, description="Max concurrent sessions per user")
    
    # Security headers
    security_headers: Dict[str, str] = Field(
        default={
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            ),
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "X-Permitted-Cross-Domain-Policies": "none"
        },
        description="Security headers"
    )
    
    # HSTS configuration
    hsts_max_age: int = Field(default=31536000, description="HSTS max age")
    hsts_include_subdomains: bool = Field(default=True, description="HSTS include subdomains")
    hsts_preload: bool = Field(default=True, description="HSTS preload")


class MonitoringConfig(BaseSettings):
    """Comprehensive monitoring configuration"""
    # OpenTelemetry
    otel_enabled: bool = Field(default=False, description="Enable OpenTelemetry")
    otel_service_name: str = Field(default="billfusion-auth-service", description="Service name")
    otel_exporter_endpoint: Optional[str] = Field(default=None, description="OTEL exporter endpoint")
    otel_insecure: bool = Field(default=True, description="OTEL insecure connection")
    
    # Prometheus metrics
    prometheus_enabled: bool = Field(default=True, description="Enable Prometheus metrics")
    prometheus_path: str = Field(default="/metrics", description="Metrics endpoint path")
    prometheus_port: Optional[int] = Field(default=None, description="Separate metrics port")
    
    # Health checks
    health_check_enabled: bool = Field(default=True, description="Enable health checks")
    health_check_timeout: int = Field(default=10, description="Health check timeout")
    health_check_interval: int = Field(default=30, description="Health check interval")
    
    # Grafana integration
    grafana_url: Optional[str] = Field(default=None, description="Grafana dashboard URL")
    grafana_api_key: Optional[str] = Field(default=None, description="Grafana API key")
    
    # Alerting
    alerting_enabled: bool = Field(default=False, description="Enable alerting")
    alert_webhook_url: Optional[str] = Field(default=None, description="Alert webhook URL")
    alert_email: Optional[str] = Field(default=None, description="Alert email address")
    
    # Logging aggregation
    log_aggregation_enabled: bool = Field(default=False, description="Enable log aggregation")
    log_aggregation_endpoint: Optional[str] = Field(default=None, description="Log aggregation endpoint")
    log_retention_days: int = Field(default=30, description="Log retention period")


class EmailConfig(BaseSettings):
    """Enhanced email configuration"""
    # SMTP settings
    smtp_host: Optional[str] = Field(default=None, description="SMTP server host")
    smtp_port: int = Field(default=587, description="SMTP server port")
    smtp_username: Optional[str] = Field(default=None, description="SMTP username")
    smtp_password: Optional[str] = Field(default=None, description="SMTP password")
    smtp_use_tls: bool = Field(default=True, description="Use TLS for SMTP")
    smtp_timeout: int = Field(default=30, description="SMTP timeout")
    
    # Email service providers
    sendgrid_api_key: Optional[str] = Field(default=None, description="SendGrid API key")
    ses_region: Optional[str] = Field(default=None, description="AWS SES region")
    ses_access_key: Optional[str] = Field(default=None, description="AWS SES access key")
    ses_secret_key: Optional[str] = Field(default=None, description="AWS SES secret key")
    
    # Email templates
    template_directory: str = Field(default="./templates/email", description="Email templates directory")
    default_from_email: str = Field(default="noreply@billfusion.com", description="Default from email")
    default_from_name: str = Field(default="BillFusion", description="Default from name")
    
    # Email features
    email_verification_enabled: bool = Field(default=True, description="Enable email verification")
    welcome_email_enabled: bool = Field(default=True, description="Send welcome emails")
    notification_emails_enabled: bool = Field(default=True, description="Send notification emails")
    
    @validator("smtp_host")
    def validate_smtp_host(cls, v):
        if v and not re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("Invalid SMTP host format")
        return v


class RateLimitingConfig(BaseSettings):
    """Advanced rate limiting configuration"""
    # Global rate limiting
    global_requests_per_minute: int = Field(default=100, description="Global requests per minute")
    global_requests_per_hour: int = Field(default=1000, description="Global requests per hour")
    
    # Endpoint-specific rate limits
    auth_requests_per_minute: int = Field(default=10, description="Auth requests per minute")
    registration_requests_per_hour: int = Field(default=5, description="Registration requests per hour")
    password_reset_requests_per_hour: int = Field(default=3, description="Password reset requests per hour")
    
    # Role-based rate limits
    admin_requests_per_minute: int = Field(default=200, description="Admin requests per minute")
    employee_requests_per_minute: int = Field(default=150, description="Employee requests per minute")
    vendor_requests_per_minute: int = Field(default=100, description="Vendor requests per minute")
    client_requests_per_minute: int = Field(default=50, description="Client requests per minute")
    
    # Rate limiting window
    rate_limit_window_seconds: int = Field(default=60, description="Rate limit window")
    
    # Exemptions
    rate_limit_exempted_ips: List[str] = Field(default=[], description="IPs exempt from rate limiting")
    rate_limit_exempted_user_agents: List[str] = Field(default=[], description="User agents exempt from rate limiting")


class FileStorageConfig(BaseSettings):
    """File storage configuration with cloud support"""
    # Local storage
    local_storage_path: str = Field(default="./uploads", description="Local file storage path")
    max_file_size_mb: int = Field(default=10, description="Maximum file size in MB")
    allowed_file_types: List[str] = Field(
        default=["jpg", "jpeg", "png", "gif", "pdf", "doc", "docx"],
        description="Allowed file types"
    )
    
    # AWS S3
    aws_s3_bucket: Optional[str] = Field(default=None, description="AWS S3 bucket name")
    aws_access_key_id: Optional[str] = Field(default=None, description="AWS access key ID")
    aws_secret_access_key: Optional[str] = Field(default=None, description="AWS secret access key")
    aws_region: str = Field(default="us-east-1", description="AWS region")
    
    # Google Cloud Storage
    gcs_bucket: Optional[str] = Field(default=None, description="Google Cloud Storage bucket")
    gcs_credentials_path: Optional[str] = Field(default=None, description="GCS credentials file path")
    
    # File processing
    image_optimization_enabled: bool = Field(default=True, description="Enable image optimization")
    virus_scanning_enabled: bool = Field(default=False, description="Enable virus scanning")
    
    @validator("allowed_file_types")
    def validate_file_types(cls, v):
        valid_extensions = {
            'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg',  # Images
            'pdf', 'doc', 'docx', 'txt', 'rtf',  # Documents
            'xls', 'xlsx', 'csv',  # Spreadsheets
            'mp4', 'avi', 'mov', 'wmv',  # Videos
            'mp3', 'wav', 'flac'  # Audio
        }
        
        invalid_types = set(v) - valid_extensions
        if invalid_types:
            raise ValueError(f"Invalid file types: {invalid_types}")
        
        return v


class Settings(BaseSettings):
    """
    Comprehensive application settings with all TODO tasks completed
    """
    
    # Basic Application Settings
    project_name: str = "BillFusion Auth Service"
    version: str = "1.0.0"
    debug: bool = Field(default=False, description="Debug mode")
    host: str = Field(default="0.0.0.0", description="Host to bind to")
    port: int = Field(default=8000, description="Port to bind to")
    
    # Environment configuration
    environment: str = Field(default="development", description="Environment (development, staging, production)")
    frontend_url: str = Field(default="http://localhost:3000", description="Frontend application URL")
    api_base_url: str = Field(default="http://localhost:8000", description="API base URL")
    
    # Component configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    oauth: OAuthConfig = Field(default_factory=OAuthConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)
    rate_limiting: RateLimitingConfig = Field(default_factory=RateLimitingConfig)
    file_storage: FileStorageConfig = Field(default_factory=FileStorageConfig)
    
    # CORS Settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )
    cors_credentials: bool = Field(default=True, description="Allow CORS credentials")
    cors_methods: List[str] = Field(default=["*"], description="Allowed CORS methods")
    cors_headers: List[str] = Field(default=["*"], description="Allowed CORS headers")
    
    # Allowed hosts
    allowed_hosts: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        description="Allowed hosts"
    )
    
    # Logging Settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json, text)")
    log_file_path: Optional[str] = Field(default=None, description="Log file path")
    log_max_size_mb: int = Field(default=100, description="Max log file size in MB")
    log_backup_count: int = Field(default=5, description="Number of log backup files")
    
    # Role-based Access Control
    default_user_role: str = Field(default="employee", description="Default role for new users")
    roles: List[str] = Field(
        default=["client", "vendor", "employee", "admin"],
        description="Available user roles"
    )
    
    # Role permissions mapping
    role_permissions: Dict[str, List[str]] = Field(
        default={
            "admin": ["*"],  # All permissions
            "employee": ["user:read", "user:write", "billing:read", "billing:write", "report:read", "report:write"],
            "vendor": ["profile:read", "profile:write", "billing:read", "billing:write", "report:read"],
            "client": ["profile:read", "profile:write", "billing:read", "report:read"]
        },
        description="Role-based permissions mapping"
    )
    
    # Hierarchical role system
    role_hierarchy: Dict[str, List[str]] = Field(
        default={
            "admin": ["employee", "vendor", "client"],
            "employee": ["vendor", "client"],
            "vendor": [],
            "client": []
        },
        description="Role hierarchy (higher roles inherit lower role permissions)"
    )
    
    # API Documentation
    api_docs_enabled: bool = Field(default=True, description="Enable API documentation")
    api_contact: Dict[str, str] = Field(
        default={
            "name": "BillFusion Team",
            "email": "support@billfusion.com",
            "url": "https://billfusion.com/support"
        },
        description="API contact information"
    )
    
    # API versioning
    api_version: str = Field(default="v1", description="Current API version")
    api_versions_supported: List[str] = Field(default=["v1"], description="Supported API versions")
    api_deprecation_warnings: bool = Field(default=True, description="Enable deprecation warnings")
    
    # Cache configuration
    cache_enabled: bool = Field(default=True, description="Enable caching")
    cache_default_ttl: int = Field(default=300, description="Default cache TTL in seconds")
    cache_user_session_ttl: int = Field(default=1800, description="User session cache TTL")
    cache_auth_token_ttl: int = Field(default=900, description="Auth token cache TTL")
    
    @validator("environment")
    def validate_environment(cls, v):
        allowed_environments = ["development", "staging", "production"]
        if v not in allowed_environments:
            raise ValueError(f"ENVIRONMENT must be one of {allowed_environments}")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"LOG_LEVEL must be one of {allowed_levels}")
        return v.upper()
    
    @validator("cors_origins")
    def validate_cors_origins(cls, v, values):
        if not isinstance(v, list):
            raise ValueError("CORS_ORIGINS must be a list")
        
        # Check for wildcard origins in production
        environment = values.get("environment", "development")
        if environment == "production" and "*" in v:
            raise ValueError("Wildcard CORS origins not allowed in production")
        
        return v
    
    @root_validator
    def validate_production_settings(cls, values):
        """Validate production-specific settings"""
        environment = values.get("environment")
        
        if environment == "production":
            # Require secure settings in production
            if values.get("debug", False):
                raise ValueError("DEBUG must be False in production")
            
            security = values.get("security", {})
            if isinstance(security, SecurityConfig):
                if security.secret_key == secrets.token_urlsafe(32):
                    raise ValueError("SECRET_KEY must be set explicitly in production")
            
            # Require HTTPS in production
            frontend_url = values.get("frontend_url", "")
            api_base_url = values.get("api_base_url", "")
            if not frontend_url.startswith("https://"):
                raise ValueError("FRONTEND_URL must use HTTPS in production")
            if not api_base_url.startswith("https://"):
                raise ValueError("API_BASE_URL must use HTTPS in production")
        
        return values
    
    def get_database_url(self) -> str:
        """Get the database connection URL"""
        return self.database.url
    
    def get_redis_url(self) -> str:
        """Get the Redis connection URL"""
        return self.redis.url
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == "development"
    
    def get_allowed_file_extensions(self) -> List[str]:
        """Get allowed file extensions"""
        return self.file_storage.allowed_file_types
    
    def get_role_permissions(self, role: str) -> List[str]:
        """Get permissions for a specific role"""
        direct_permissions = self.role_permissions.get(role, [])
        
        # Add inherited permissions from role hierarchy
        inherited_roles = self.role_hierarchy.get(role, [])
        all_permissions = set(direct_permissions)
        
        for inherited_role in inherited_roles:
            all_permissions.update(self.role_permissions.get(inherited_role, []))
        
        return list(all_permissions)
    
    def has_permission(self, role: str, permission: str) -> bool:
        """Check if a role has a specific permission"""
        role_permissions = self.get_role_permissions(role)
        return "*" in role_permissions or permission in role_permissions
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        env_nested_delimiter = "__"  # For nested config like DATABASE__URL
        validate_assignment = True


# Create settings instance with enhanced validation
def create_settings() -> Settings:
    """Create and validate settings instance"""
    try:
        settings = Settings()
        
        # Validate configuration on startup
        if settings.is_production():
            print("🔒 Running in PRODUCTION mode with enhanced security")
        else:
            print(f"🔧 Running in {settings.environment.upper()} mode")
        
        # Log configuration status
        print(f"📊 Monitoring: {'Enabled' if settings.monitoring.prometheus_enabled else 'Disabled'}")
        print(f"📧 Email Service: {'Configured' if settings.email.smtp_host else 'Not Configured'}")
        print(f"🗄️ Redis Cache: {'Enabled' if settings.cache_enabled else 'Disabled'}")
        print(f"🔐 OAuth Providers: {len([p for p in ['google', 'microsoft', 'apple', 'github'] if getattr(settings.oauth, f'{p}_client_id')])}")
        
        return settings
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        raise


# Global settings instance
settings = create_settings()


# Backward compatibility aliases
DATABASE_URL = settings.get_database_url()
REDIS_URL = settings.get_redis_url()
SECRET_KEY = settings.security.secret_key
ACCESS_TOKEN_EXPIRE_MINUTES = settings.security.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.security.refresh_token_expire_days
ALGORITHM = settings.security.algorithm
DEBUG = settings.debug
ENVIRONMENT = settings.environment
CORS_ORIGINS = settings.cors_origins
ALLOWED_HOSTS = settings.allowed_hosts
DEFAULT_USER_ROLE = settings.default_user_role
GOOGLE_CLIENT_ID = settings.oauth.google_client_id
GOOGLE_CLIENT_SECRET = settings.oauth.google_client_secret
SMTP_HOST = settings.email.smtp_host
SMTP_PORT = settings.email.smtp_port
SMTP_USERNAME = settings.email.smtp_username
SMTP_PASSWORD = settings.email.smtp_password
SMTP_USE_TLS = settings.email.smtp_use_tls
RATE_LIMIT_REQUESTS = settings.rate_limiting.global_requests_per_minute
RATE_LIMIT_WINDOW = settings.rate_limiting.rate_limit_window_seconds
SECURITY_HEADERS = settings.security.security_headers
DATABASE_POOL_SIZE = settings.database.pool_size
DATABASE_MAX_OVERFLOW = settings.database.max_overflow
FRONTEND_URL = settings.frontend_url
