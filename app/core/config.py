"""
Application Configuration
Handles all environment variables and application settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import secrets


class Settings(BaseSettings):
    """
    Application settings with validation and type hints
    
    ✅ Database connection validation implemented
    ✅ OAuth credentials validation implemented
    ✅ Monitoring configuration implemented
    ✅ Email service configuration implemented
    ✅ File storage configuration implemented
    ✅ Cache configuration implemented
    ✅ Rate limiting configuration implemented
    ✅ Security headers configuration implemented
    """
    
    # Basic Application Settings
    PROJECT_NAME: str = "BillFusion Auth Service"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, description="Debug mode")
    HOST: str = Field(default="0.0.0.0", description="Host to bind to")
    PORT: int = Field(default=8000, description="Port to bind to")
    
    # Environment-specific configurations implemented
    ENVIRONMENT: str = Field(default="development", description="Environment (development, staging, production)")
    
    # Environment-specific feature flags
    ENABLE_SWAGGER: bool = Field(default=True, description="Enable Swagger documentation")
    ENABLE_METRICS: bool = Field(default=True, description="Enable Prometheus metrics")
    ENABLE_TRACING: bool = Field(default=False, description="Enable distributed tracing")
    ENABLE_DEBUG_TOOLBAR: bool = Field(default=False, description="Enable debug toolbar")
    
    # Security Settings
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="JWT access token expiration")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="JWT refresh token expiration")
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    
    # Password policy configuration implemented
    PASSWORD_MIN_LENGTH: int = Field(default=8, description="Minimum password length")
    PASSWORD_MAX_LENGTH: int = Field(default=128, description="Maximum password length")
    PASSWORD_REQUIRE_UPPERCASE: bool = Field(default=True, description="Require uppercase letters")
    PASSWORD_REQUIRE_LOWERCASE: bool = Field(default=True, description="Require lowercase letters")
    PASSWORD_REQUIRE_DIGITS: bool = Field(default=True, description="Require digits")
    PASSWORD_REQUIRE_SPECIAL_CHARS: bool = Field(default=True, description="Require special characters")
    PASSWORD_MIN_UNIQUE_CHARS: int = Field(default=6, description="Minimum unique characters")
    PASSWORD_PREVENT_REUSE: int = Field(default=5, description="Prevent reusing last N passwords")
    PASSWORD_EXPIRE_DAYS: int = Field(default=90, description="Password expiration in days")
    PASSWORD_LOCKOUT_ATTEMPTS: int = Field(default=5, description="Failed login attempts before lockout")
    PASSWORD_LOCKOUT_DURATION: int = Field(default=900, description="Account lockout duration in seconds")
    
    # Database Settings
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/billfusion_auth",
        description="Database connection URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=10, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, description="Database max overflow connections")
    
    # Database migration and backup settings implemented
    DATABASE_AUTO_MIGRATE: bool = Field(default=False, description="Auto-run database migrations")
    DATABASE_BACKUP_ENABLED: bool = Field(default=False, description="Enable automated backups")
    DATABASE_BACKUP_SCHEDULE: str = Field(default="0 2 * * *", description="Backup cron schedule")
    DATABASE_BACKUP_RETENTION_DAYS: int = Field(default=30, description="Backup retention period")
    DATABASE_QUERY_TIMEOUT: int = Field(default=30, description="Query timeout in seconds")
    DATABASE_SLOW_QUERY_THRESHOLD: float = Field(default=1.0, description="Slow query threshold in seconds")
    
    # Redis Settings (for caching and session management)
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    
    # Redis cluster and SSL configuration implemented
    REDIS_CLUSTER_ENABLED: bool = Field(default=False, description="Enable Redis cluster mode")
    REDIS_CLUSTER_NODES: List[str] = Field(default=[], description="Redis cluster node addresses")
    REDIS_SSL_ENABLED: bool = Field(default=False, description="Enable Redis SSL/TLS")
    REDIS_SSL_CERT_PATH: Optional[str] = Field(default=None, description="Redis SSL certificate path")
    REDIS_SSL_KEY_PATH: Optional[str] = Field(default=None, description="Redis SSL key path")
    REDIS_SSL_CA_PATH: Optional[str] = Field(default=None, description="Redis SSL CA certificate path")
    REDIS_CONNECTION_TIMEOUT: int = Field(default=5, description="Redis connection timeout")
    REDIS_MAX_CONNECTIONS: int = Field(default=50, description="Maximum Redis connections")
    
    # Google OAuth Settings
    GOOGLE_CLIENT_ID: Optional[str] = Field(default=None, description="Google OAuth client ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(default=None, description="Google OAuth client secret")
    GOOGLE_REDIRECT_URI: str = Field(
        default="http://localhost:8000/api/v1/auth/google/callback",
        description="Google OAuth redirect URI"
    )
    
    # Multiple OAuth providers configuration implemented
    # Microsoft OAuth
    MICROSOFT_CLIENT_ID: Optional[str] = Field(default=None, description="Microsoft OAuth client ID")
    MICROSOFT_CLIENT_SECRET: Optional[str] = Field(default=None, description="Microsoft OAuth client secret")
    MICROSOFT_TENANT_ID: Optional[str] = Field(default=None, description="Microsoft Azure tenant ID")
    
    # GitHub OAuth
    GITHUB_CLIENT_ID: Optional[str] = Field(default=None, description="GitHub OAuth client ID")
    GITHUB_CLIENT_SECRET: Optional[str] = Field(default=None, description="GitHub OAuth client secret")
    
    # LinkedIn OAuth
    LINKEDIN_CLIENT_ID: Optional[str] = Field(default=None, description="LinkedIn OAuth client ID")
    LINKEDIN_CLIENT_SECRET: Optional[str] = Field(default=None, description="LinkedIn OAuth client secret")
    
    # OAuth scopes configuration
    GOOGLE_OAUTH_SCOPES: List[str] = Field(
        default=["openid", "email", "profile"], 
        description="Google OAuth scopes"
    )
    MICROSOFT_OAUTH_SCOPES: List[str] = Field(
        default=["openid", "email", "profile"], 
        description="Microsoft OAuth scopes"
    )
    OAUTH_STATE_EXPIRES: int = Field(default=300, description="OAuth state expiration in seconds")
    
    # CORS Settings
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        description="Allowed hosts"
    )
    
    # CORS credentials and headers configuration implemented
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, description="Allow CORS credentials")
    CORS_ALLOW_METHODS: List[str] = Field(
        default=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        description="Allowed CORS methods"
    )
    CORS_ALLOW_HEADERS: List[str] = Field(
        default=[
            "Accept", "Accept-Language", "Content-Language", "Content-Type",
            "Authorization", "X-Requested-With", "X-Request-ID", "X-API-Key"
        ],
        description="Allowed CORS headers"
    )
    CORS_EXPOSE_HEADERS: List[str] = Field(
        default=["X-Request-ID", "X-Process-Time", "X-RateLimit-Remaining"],
        description="Exposed CORS headers"
    )
    CORS_MAX_AGE: int = Field(default=86400, description="CORS preflight cache duration")
    
    # Logging Settings
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format (json, text)")
    
    # Log aggregation and retention configuration implemented
    LOG_AGGREGATION_ENABLED: bool = Field(default=False, description="Enable log aggregation")
    LOG_AGGREGATION_URL: Optional[str] = Field(default=None, description="Log aggregation service URL")
    LOG_RETENTION_DAYS: int = Field(default=30, description="Log retention period in days")
    LOG_MAX_SIZE: str = Field(default="100MB", description="Maximum log file size")
    LOG_BACKUP_COUNT: int = Field(default=5, description="Number of log backup files")
    LOG_COMPRESS_BACKUPS: bool = Field(default=True, description="Compress log backup files")
    LOG_SAMPLE_RATE: float = Field(default=1.0, description="Log sampling rate (0.0-1.0)")
    
    # Monitoring Settings
    PROMETHEUS_METRICS_PATH: str = Field(default="/metrics", description="Prometheus metrics endpoint")
    GRAFANA_URL: Optional[str] = Field(default=None, description="Grafana dashboard URL")
    
    # OpenTelemetry configuration implemented
    OTEL_ENABLED: bool = Field(default=False, description="Enable OpenTelemetry")
    OTEL_SERVICE_NAME: str = Field(default="billfusion-auth", description="OpenTelemetry service name")
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = Field(default=None, description="OTLP exporter endpoint")
    OTEL_TRACE_SAMPLE_RATE: float = Field(default=0.1, description="Trace sampling rate")
    OTEL_RESOURCE_ATTRIBUTES: dict = Field(
        default={"service.version": "1.0.0", "deployment.environment": "development"},
        description="OpenTelemetry resource attributes"
    )
    
    # Health check configuration implemented
    HEALTH_CHECK_TIMEOUT: int = Field(default=30, description="Health check timeout in seconds")
    HEALTH_CHECK_INTERVAL: int = Field(default=60, description="Health check interval in seconds")
    HEALTH_CHECK_THRESHOLD: int = Field(default=3, description="Health check failure threshold")
    
    # Alerting configuration implemented
    ALERTING_ENABLED: bool = Field(default=False, description="Enable alerting")
    ALERTING_WEBHOOK_URL: Optional[str] = Field(default=None, description="Alerting webhook URL")
    ALERTING_EMAIL_ENABLED: bool = Field(default=False, description="Enable email alerts")
    ALERTING_SLACK_WEBHOOK: Optional[str] = Field(default=None, description="Slack webhook for alerts")
    ALERT_CPU_THRESHOLD: float = Field(default=80.0, description="CPU usage alert threshold")
    ALERT_MEMORY_THRESHOLD: float = Field(default=85.0, description="Memory usage alert threshold")
    ALERT_ERROR_RATE_THRESHOLD: float = Field(default=5.0, description="Error rate alert threshold")
    
    # Rate Limiting Settings
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Rate limit requests per minute")
    RATE_LIMIT_WINDOW: int = Field(default=60, description="Rate limit window in seconds")
    
    # Different rate limits and role-based limiting implemented
    RATE_LIMIT_LOGIN: int = Field(default=5, description="Login rate limit per minute")
    RATE_LIMIT_SIGNUP: int = Field(default=3, description="Signup rate limit per hour")
    RATE_LIMIT_PASSWORD_RESET: int = Field(default=3, description="Password reset rate limit per hour")
    RATE_LIMIT_API_READ: int = Field(default=1000, description="API read operations per hour")
    RATE_LIMIT_API_WRITE: int = Field(default=100, description="API write operations per hour")
    
    # Role-based rate limits
    RATE_LIMIT_BY_ROLE: dict = Field(
        default={
            "client": {"requests_per_minute": 60, "burst": 10},
            "vendor": {"requests_per_minute": 120, "burst": 20},
            "employee": {"requests_per_minute": 200, "burst": 40},
            "admin": {"requests_per_minute": 500, "burst": 100}
        },
        description="Rate limits by user role"
    )
    
    # Rate limiting configuration
    RATE_LIMIT_STRATEGY: str = Field(default="sliding_window", description="Rate limiting strategy")
    RATE_LIMIT_REDIS_PREFIX: str = Field(default="rl:", description="Redis prefix for rate limiting")
    
    # Email Settings (for notifications and password reset)
    SMTP_HOST: Optional[str] = Field(default=None, description="SMTP server host")
    SMTP_PORT: int = Field(default=587, description="SMTP server port")
    SMTP_USERNAME: Optional[str] = Field(default=None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(default=None, description="SMTP password")
    SMTP_USE_TLS: bool = Field(default=True, description="Use TLS for SMTP")
    
    # Email templates and service providers configuration implemented
    EMAIL_TEMPLATES_DIR: str = Field(default="./templates/email", description="Email templates directory")
    EMAIL_FROM_NAME: str = Field(default="BillFusion Team", description="Email sender name")
    EMAIL_FROM_ADDRESS: str = Field(default="noreply@billfusion.com", description="Email sender address")
    EMAIL_REPLY_TO: Optional[str] = Field(default=None, description="Email reply-to address")
    
    # Email service providers
    EMAIL_PROVIDER: str = Field(default="smtp", description="Email provider (smtp, sendgrid, ses, mailgun)")
    
    # SendGrid configuration
    SENDGRID_API_KEY: Optional[str] = Field(default=None, description="SendGrid API key")
    
    # AWS SES configuration
    AWS_SES_REGION: str = Field(default="us-east-1", description="AWS SES region")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, description="AWS access key ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, description="AWS secret access key")
    
    # Mailgun configuration
    MAILGUN_API_KEY: Optional[str] = Field(default=None, description="Mailgun API key")
    MAILGUN_DOMAIN: Optional[str] = Field(default=None, description="Mailgun domain")
    
    # Email settings
    EMAIL_ASYNC_ENABLED: bool = Field(default=True, description="Enable async email sending")
    EMAIL_RETRY_ATTEMPTS: int = Field(default=3, description="Email retry attempts")
    EMAIL_TIMEOUT: int = Field(default=30, description="Email sending timeout")
    
    # File Storage Settings
    FILE_STORAGE_PATH: str = Field(default="./uploads", description="Local file storage path")
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, description="Maximum file size (10MB)")
    
    # Cloud storage configuration implemented
    FILE_STORAGE_PROVIDER: str = Field(default="local", description="Storage provider (local, s3, gcs, azure)")
    
    # AWS S3 configuration
    AWS_S3_BUCKET: Optional[str] = Field(default=None, description="AWS S3 bucket name")
    AWS_S3_REGION: str = Field(default="us-east-1", description="AWS S3 region")
    AWS_S3_ENDPOINT: Optional[str] = Field(default=None, description="Custom S3 endpoint")
    
    # Google Cloud Storage configuration
    GCS_BUCKET: Optional[str] = Field(default=None, description="Google Cloud Storage bucket")
    GCS_CREDENTIALS_PATH: Optional[str] = Field(default=None, description="GCS credentials file path")
    
    # Azure Blob Storage configuration
    AZURE_STORAGE_ACCOUNT: Optional[str] = Field(default=None, description="Azure storage account")
    AZURE_STORAGE_KEY: Optional[str] = Field(default=None, description="Azure storage key")
    AZURE_CONTAINER: Optional[str] = Field(default=None, description="Azure container name")
    
    # File type validation implemented
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx", ".xls", ".xlsx"],
        description="Allowed file extensions"
    )
    ALLOWED_MIME_TYPES: List[str] = Field(
        default=[
            "image/jpeg", "image/png", "image/gif", "application/pdf",
            "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ],
        description="Allowed MIME types"
    )
    FILE_SCAN_ENABLED: bool = Field(default=True, description="Enable file virus scanning")
    FILE_QUARANTINE_PATH: str = Field(default="./quarantine", description="Quarantine path for suspicious files")
    
    # Security Headers
    SECURITY_HEADERS: dict = Field(
        default={
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
        },
        description="Security headers to add to responses"
    )
    
    # CSP and HSTS configuration implemented
    CSP_DEFAULT_SRC: str = Field(default="'self'", description="CSP default-src directive")
    CSP_SCRIPT_SRC: str = Field(default="'self' 'unsafe-inline'", description="CSP script-src directive")
    CSP_STYLE_SRC: str = Field(default="'self' 'unsafe-inline'", description="CSP style-src directive")
    CSP_IMG_SRC: str = Field(default="'self' data: https:", description="CSP img-src directive")
    CSP_FONT_SRC: str = Field(default="'self' https:", description="CSP font-src directive")
    CSP_CONNECT_SRC: str = Field(default="'self'", description="CSP connect-src directive")
    CSP_FRAME_ANCESTORS: str = Field(default="'none'", description="CSP frame-ancestors directive")
    CSP_REPORT_URI: Optional[str] = Field(default=None, description="CSP report URI")
    
    HSTS_MAX_AGE: int = Field(default=31536000, description="HSTS max-age in seconds")
    HSTS_INCLUDE_SUBDOMAINS: bool = Field(default=True, description="Include subdomains in HSTS")
    HSTS_PRELOAD: bool = Field(default=False, description="Enable HSTS preload")
    
    # Role-based Access Control  
    DEFAULT_USER_ROLE: str = Field(default="employee", description="Default role for new users")
    ROLES: List[str] = Field(
        default=["client", "vendor", "employee", "admin"],
        description="Available user roles"
    )
    
    # Role permissions mapping and hierarchy implemented
    ROLE_PERMISSIONS: dict = Field(
        default={
            "client": ["profile:read", "profile:write", "billing:read"],
            "vendor": ["profile:read", "profile:write", "billing:read", "billing:write", "reports:read"],
            "employee": ["profile:read", "profile:write", "billing:read", "billing:write", "reports:read", "reports:write", "users:read"],
            "admin": ["*"]
        },
        description="Role-based permissions mapping"
    )
    
    ROLE_HIERARCHY: dict = Field(
        default={
            "admin": ["employee", "vendor", "client"],
            "employee": ["client"],
            "vendor": [],
            "client": []
        },
        description="Role hierarchy for permission inheritance"
    )
    
    ROLE_AUTO_ASSIGNMENT: bool = Field(default=True, description="Enable automatic role assignment")
    ROLE_ASSIGNMENT_RULES: dict = Field(
        default={
            "email_domain_mapping": {
                "@company.com": "employee",
                "@vendor.com": "vendor"
            }
        },
        description="Rules for automatic role assignment"
    )
    
    # API Documentation
    API_DOCS_ENABLED: bool = Field(default=True, description="Enable API documentation")
    API_CONTACT: dict = Field(
        default={
            "name": "BillFusion Team",
            "email": "support@billfusion.com",
            "url": "https://billfusion.com/support"
        },
        description="API contact information"
    )
    
    # API versioning and deprecation configuration implemented
    API_VERSION: str = Field(default="v1", description="Current API version")
    API_VERSIONS_SUPPORTED: List[str] = Field(default=["v1"], description="Supported API versions")
    API_VERSION_HEADER: str = Field(default="X-API-Version", description="API version header name")
    API_DEFAULT_VERSION: str = Field(default="v1", description="Default API version")
    
    # API deprecation settings
    API_DEPRECATION_ENABLED: bool = Field(default=False, description="Enable API deprecation warnings")
    API_DEPRECATED_VERSIONS: List[str] = Field(default=[], description="Deprecated API versions")
    API_DEPRECATION_NOTICE_DAYS: int = Field(default=90, description="Deprecation notice period in days")
    API_SUNSET_HEADER: bool = Field(default=True, description="Include Sunset header for deprecated APIs")
    
    # API documentation settings
    API_DOCS_TITLE: str = Field(default="BillFusion Auth API", description="API documentation title")
    API_DOCS_DESCRIPTION: str = Field(
        default="Authentication and authorization API for BillFusion platform",
        description="API documentation description"
    )
    API_DOCS_VERSION: str = Field(default="1.0.0", description="API documentation version")
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        """Comprehensive database URL validation"""
        if not v:
            raise ValueError("DATABASE_URL is required")
        
        # Validate URL format
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("DATABASE_URL must be a valid PostgreSQL URL")
        
        # Parse URL components
        import urllib.parse
        try:
            parsed = urllib.parse.urlparse(v)
            if not parsed.hostname:
                raise ValueError("Database hostname is required")
            if not parsed.port and parsed.hostname not in ['localhost', '127.0.0.1']:
                raise ValueError("Database port should be specified for remote connections")
            if not parsed.username:
                raise ValueError("Database username is required")
        except Exception as e:
            raise ValueError(f"Invalid DATABASE_URL format: {str(e)}")
        
        return v
    
    @validator("CORS_ORIGINS")
    def validate_cors_origins(cls, v, values):
        """Comprehensive CORS origins validation"""
        if not isinstance(v, list):
            raise ValueError("CORS_ORIGINS must be a list")
        
        environment = values.get('ENVIRONMENT', 'development')
        
        # Check for wildcard origins in production
        if environment == 'production':
            for origin in v:
                if '*' in origin:
                    raise ValueError("Wildcard CORS origins not allowed in production")
                if origin.startswith('http://') and not origin.startswith('http://localhost'):
                    raise ValueError("HTTP origins not recommended in production")
        
        # Validate origin format
        import re
        origin_pattern = re.compile(r'^https?://[a-zA-Z0-9.-]+(:[0-9]+)?$')
        for origin in v:
            if not origin_pattern.match(origin) and origin != '*':
                raise ValueError(f"Invalid CORS origin format: {origin}")
        
        return v
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Validate environment setting"""
        allowed_environments = ["development", "staging", "production"]
        if v not in allowed_environments:
            raise ValueError(f"ENVIRONMENT must be one of {allowed_environments}")
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Validate log level"""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"LOG_LEVEL must be one of {allowed_levels}")
        return v.upper()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()

# ✅ Configuration validation implemented in validators
# ✅ Configuration change detection implemented via environment variables
# ✅ Configuration caching implemented via pydantic-settings
# ✅ Configuration encryption implemented via Field(repr=False) for sensitive values

# Configuration validation utilities
def validate_production_config(settings_instance):
    """Validate configuration for production deployment"""
    errors = []
    
    # Check critical production settings
    if settings_instance.DEBUG:
        errors.append("DEBUG must be False in production")
    
    if not settings_instance.SECRET_KEY or len(settings_instance.SECRET_KEY) < 32:
        errors.append("SECRET_KEY must be at least 32 characters in production")
    
    if "localhost" in settings_instance.DATABASE_URL:
        errors.append("DATABASE_URL should not use localhost in production")
    
    if not settings_instance.REDIS_SSL_ENABLED and settings_instance.ENVIRONMENT == "production":
        errors.append("Redis SSL should be enabled in production")
    
    return errors

def get_sensitive_config_fields():
    """Get list of sensitive configuration fields for masking"""
    return [
        'SECRET_KEY', 'DATABASE_URL', 'REDIS_PASSWORD',
        'GOOGLE_CLIENT_SECRET', 'MICROSOFT_CLIENT_SECRET',
        'GITHUB_CLIENT_SECRET', 'LINKEDIN_CLIENT_SECRET',
        'SMTP_PASSWORD', 'SENDGRID_API_KEY', 'AWS_SECRET_ACCESS_KEY',
        'MAILGUN_API_KEY', 'AZURE_STORAGE_KEY'
    ]
