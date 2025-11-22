# BillFusion Authentication Service

A comprehensive authentication and authorization service for the BillFusion Unified Billing & Reporting Platform. This service supports multiple user roles (Client, Vendor, Employee, Admin) with JWT authentication, Google OAuth, role-based access control, and comprehensive monitoring.

## 🚀 Features

### Authentication & Authorization
- **Multi-role Support**: Client, Vendor, Employee, Admin roles
- **JWT Authentication**: Secure token-based authentication with refresh tokens
- **Google OAuth**: Social login integration
- **Role-Based Access Control (RBAC)**: Fine-grained permissions system
- **Session Management**: Secure session tracking and management
- **Password Security**: Bcrypt hashing with configurable policies

### Security Features
- **Input Sanitization**: Protection against injection attacks
- **Rate Limiting**: Redis-based rate limiting with sliding window
- **Security Headers**: Comprehensive security headers
- **Audit Logging**: Complete audit trail for compliance
- **Account Lockout**: Brute force protection
- **Two-Factor Authentication**: TOTP-based 2FA (TODO)

### Monitoring & Observability
- **Structured Logging**: JSON-based logging with correlation IDs
- **Prometheus Metrics**: Application and infrastructure metrics
- **Grafana Dashboards**: Real-time monitoring dashboards
- **Health Checks**: Comprehensive health monitoring
- **Distributed Tracing**: OpenTelemetry integration (TODO)

### Infrastructure
- **Docker Containerization**: Multi-stage Docker builds
- **Docker Compose**: Complete development environment
- **PostgreSQL**: Async database with connection pooling
- **Redis**: Caching and session storage
- **Nginx**: Reverse proxy and load balancing (optional)

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │────│  Auth Service   │────│   PostgreSQL    │
│  (React/Vue)    │    │   (FastAPI)     │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ├─────────────────┐
                              │     Redis       │
                              │   (Sessions)    │
                              └─────────────────┘
                              │
                       ┌──────┴──────┐
                       │ Monitoring  │
                       │ (Prometheus │
                       │ + Grafana)  │
                       └─────────────┘
```

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 15+ (if running locally)
- Redis 7+ (if running locally)

## 🚀 Quick Start

### 1. Clone and Setup Environment

```bash
cd d:/Projects/BillPlatform/auth-service
cp .env.example .env
# Edit .env with your configuration
```

### 2. Start with Docker Compose

```bash
# Start all services
docker-compose up --build

# Or start in background
docker-compose up -d --build
```

### 3. Access Services

- **Auth Service API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Grafana Dashboard**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **Database**: localhost:5432 (postgres/postgres123)
- **Redis**: localhost:6379

## 🛠️ Development Setup

### Local Development (with virtual environment)

```bash
# Activate existing virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://postgres:postgres123@localhost:5432/billfusion_auth"
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="your-secret-key"

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Migrations

```bash
# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 📊 API Documentation

### Authentication Endpoints

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/google` - Google OAuth login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/change-password` - Change password
- `POST /api/v1/auth/forgot-password` - Request password reset
- `POST /api/v1/auth/reset-password` - Reset password
- `POST /api/v1/auth/verify-email` - Verify email address

### User Management Endpoints

- `GET /api/v1/users/` - List users (requires USER_READ)
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user
- `POST /api/v1/users/{user_id}/activate` - Activate user
- `POST /api/v1/users/{user_id}/suspend` - Suspend user

### Admin Endpoints

- `GET /api/v1/admin/dashboard` - Admin dashboard data
- `GET /api/v1/admin/users/analytics` - User analytics
- `GET /api/v1/admin/audit-logs` - System audit logs
- `GET /api/v1/admin/system/health` - System health check
- `POST /api/v1/admin/system/maintenance` - Maintenance operations
- `GET /api/v1/admin/sessions` - List active sessions
- `DELETE /api/v1/admin/sessions/{session_id}` - Revoke session

## 🔒 Security Configuration

### Environment Variables

```bash
# Security
SECRET_KEY="your-super-secret-key-32-chars-minimum"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Password Policy
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_SPECIAL_CHARS=true

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# CORS
CORS_ORIGINS='["http://localhost:3000","https://yourdomain.com"]'
ALLOWED_HOSTS='["localhost","yourdomain.com"]'
```

### User Roles and Permissions

#### Client Role
- Profile management
- View billing information
- View reports

#### Vendor Role
- Profile management
- Manage billing
- Vendor-specific operations
- View reports

#### Employee Role
- User management (read/write)
- Billing management
- Generate reports
- Employee-specific operations

#### Admin Role
- Full system access
- User administration
- System configuration
- Audit log access
- System maintenance

## 📊 Monitoring

### Prometheus Metrics

- HTTP request metrics (rate, duration, status codes)
- Authentication metrics (login attempts, failures)
- Database connection pool metrics
- Redis connection metrics
- System resource metrics

### Grafana Dashboards

- **Auth Service Overview**: Request rates, response times, error rates
- **User Activity**: Login trends, user registrations, active users
- **System Health**: Database status, Redis status, system resources
- **Security Metrics**: Failed logins, rate limiting, suspicious activity

### Log Analysis

Structured JSON logs with:
- Correlation IDs for request tracing
- Security event logging
- Performance metrics
- Error tracking with stack traces

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

### Test Categories

- **Unit Tests**: Individual function testing
- **Integration Tests**: API endpoint testing
- **Security Tests**: Authentication and authorization testing
- **Performance Tests**: Load testing with locust (TODO)

## 🚀 Deployment

### Production Docker Compose

```bash
# Use production profile
docker-compose --profile production up -d
```

### Kubernetes Deployment (TODO)

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n billfusion
```

### Environment-Specific Configuration

- **Development**: Debug enabled, detailed logging
- **Staging**: Production-like environment with test data
- **Production**: Optimized performance, security hardened

## 🔧 Configuration

### Database Configuration

```bash
DATABASE_URL="postgresql+asyncpg://username:password@host:port/database"
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
```

### Redis Configuration

```bash
REDIS_URL="redis://username:password@host:port/db"
REDIS_PASSWORD="secure-password"
```

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Set redirect URI: `http://localhost:8000/api/v1/auth/google/callback`
6. Update environment variables:

```bash
GOOGLE_CLIENT_ID="your-client-id"
GOOGLE_CLIENT_SECRET="your-client-secret"
GOOGLE_REDIRECT_URI="http://localhost:8000/api/v1/auth/google/callback"
```

## 📝 TODO Implementation Guide

The codebase contains extensive TODO comments for future implementation. Key areas include:

### High Priority TODOs
1. **Email Service Integration**: Complete email sending functionality
2. **Password Reset Flow**: Implement token generation and validation
3. **Two-Factor Authentication**: Add TOTP support
4. **Session Management**: Complete session validation and cleanup
5. **Rate Limiting**: Implement comprehensive rate limiting middleware

### Medium Priority TODOs
1. **Advanced Security**: Add device fingerprinting, fraud detection
2. **Monitoring Enhancement**: Add distributed tracing, advanced metrics
3. **User Management**: Add bulk operations, user analytics
4. **API Enhancements**: Add API versioning, deprecation handling

### Low Priority TODOs
1. **Performance Optimization**: Add caching, query optimization
2. **Additional OAuth Providers**: Microsoft, Apple, GitHub
3. **Advanced Reporting**: User behavior analytics
4. **Compliance Features**: GDPR, HIPAA compliance tools

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add type hints to all functions
- Write comprehensive tests
- Update documentation
- Add structured logging
- Include security considerations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` endpoint when running
- **Issues**: Create an issue on GitHub
- **Email**: support@billfusion.com
- **Monitoring**: Check Grafana dashboards for system health

## 🔄 Changelog

### Version 1.0.0 (Current)
- Initial release with basic authentication
- JWT token support
- Google OAuth integration
- Role-based access control
- Basic monitoring setup
- Docker containerization

### Planned Updates
- Two-factor authentication
- Advanced security features
- Enhanced monitoring
- Performance optimizations
- Mobile app support
