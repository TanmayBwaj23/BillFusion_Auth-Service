# BillFusion Auth Service - Setup Guide

This guide will help you set up and run the BillFusion Authentication Service locally or in production.

## 🎯 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git (to clone the repository)
- Make (optional, for easier commands)

### 1-Minute Setup

```bash
# Navigate to auth service directory
cd d:/Projects/BillPlatform/auth-service

# Copy environment file and edit as needed
cp .env.example .env

# Start all services
docker-compose up --build

# Access the services:
# - Auth Service API: http://localhost:8000
# - API Documentation: http://localhost:8000/docs
# - Grafana Dashboard: http://localhost:3000 (admin/admin123)
# - Prometheus Metrics: http://localhost:9090
```

## 🛠️ Detailed Setup

### Step 1: Environment Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your configuration:
   ```bash
   # Required: Change these for security
   SECRET_KEY=your-super-secret-key-change-this
   POSTGRES_PASSWORD=your-secure-db-password
   REDIS_PASSWORD=your-secure-redis-password
   
   # Optional: Google OAuth (if you want social login)
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   
   # Optional: Email service (for notifications)
   SMTP_HOST=smtp.gmail.com
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

### Step 2: Build and Start Services

Using Docker Compose:
```bash
# Build and start all services
docker-compose up --build -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f auth-service
```

Using Make (if available):
```bash
# Build images
make build

# Start services
make up

# View logs
make logs
```

### Step 3: Initialize Database

The database will be automatically initialized when the service starts. If you need to run migrations manually:

```bash
# Run database migrations
docker-compose exec auth-service alembic upgrade head

# Or using Make
make migrate
```

### Step 4: Create Admin User

An admin user is automatically created with these default credentials:
- **Email**: admin@billfusion.com
- **Password**: AdminPassword123!

You can customize this by setting environment variables:
```bash
ADMIN_EMAIL=your-admin@domain.com
ADMIN_PASSWORD=YourSecurePassword123!
```

### Step 5: Verify Setup

1. **Health Check**: Visit http://localhost:8000/health
2. **API Documentation**: Visit http://localhost:8000/docs
3. **Test Authentication**: Try registering a new user
4. **Monitor Services**: Visit http://localhost:3000 (Grafana)

## 🔧 Development Setup

### Local Development (without Docker)

1. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Required Services**:
   ```bash
   # Start only database and Redis
   docker-compose up postgres redis -d
   ```

4. **Run Application**:
   ```bash
   # Set environment variables
   export DATABASE_URL="postgresql+asyncpg://postgres:postgres123@localhost:5432/billfusion_auth"
   export REDIS_URL="redis://localhost:6379/0"
   export SECRET_KEY="your-secret-key"
   
   # Run migrations
   alembic upgrade head
   
   # Start application
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Set authorized redirect URI: `http://localhost:8000/api/v1/auth/google/callback`
6. Update your `.env` file with the credentials

## 🧪 Testing

### Run Tests

```bash
# Using Docker
docker-compose exec auth-service pytest

# With coverage
docker-compose exec auth-service pytest --cov=app --cov-report=html

# Using Make
make test
make test-cov

# Local testing (if venv is set up)
pytest
```

### Manual Testing

1. **Register User**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "TestPassword123!",
       "password_confirm": "TestPassword123!",
       "first_name": "Test",
       "last_name": "User",
       "terms_accepted": true
     }'
   ```

2. **Login User**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "TestPassword123!"
     }'
   ```

## 📊 Monitoring Setup

### Grafana Dashboard

1. Access Grafana: http://localhost:3000
2. Login with: admin/admin123
3. Navigate to Dashboards → BillFusion Auth Service
4. View metrics for:
   - Request rates and response times
   - Authentication success/failure rates
   - Database and Redis performance
   - System resource usage

### Prometheus Metrics

1. Access Prometheus: http://localhost:9090
2. Explore available metrics
3. Create custom queries and alerts

### Application Logs

```bash
# View real-time logs
docker-compose logs -f auth-service

# View specific service logs
docker-compose logs postgres
docker-compose logs redis
docker-compose logs grafana
```

## 🚀 Production Deployment

### Environment-Specific Configuration

1. **Create production environment file**:
   ```bash
   cp .env.example .env.prod
   ```

2. **Update production settings**:
   ```bash
   ENVIRONMENT=production
   DEBUG=false
   SECRET_KEY=your-super-secure-production-key
   DATABASE_URL=postgresql+asyncpg://user:pass@prod-db:5432/billfusion_auth
   CORS_ORIGINS=["https://yourdomain.com"]
   ```

3. **Use production compose file**:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

### Security Checklist

- [ ] Change all default passwords
- [ ] Set strong SECRET_KEY
- [ ] Configure HTTPS/SSL certificates
- [ ] Set up firewall rules
- [ ] Enable database SSL
- [ ] Configure backup strategy
- [ ] Set up monitoring alerts
- [ ] Review CORS origins
- [ ] Enable rate limiting
- [ ] Configure log retention

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Failed**:
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps postgres
   
   # Check database logs
   docker-compose logs postgres
   
   # Verify connection string in .env
   ```

2. **Redis Connection Failed**:
   ```bash
   # Check if Redis is running
   docker-compose ps redis
   
   # Check Redis logs
   docker-compose logs redis
   
   # Test Redis connection
   docker-compose exec redis redis-cli ping
   ```

3. **Migration Issues**:
   ```bash
   # Reset database and run migrations
   make db-reset
   
   # Or manually
   docker-compose exec auth-service alembic downgrade base
   docker-compose exec auth-service alembic upgrade head
   ```

4. **Port Conflicts**:
   ```bash
   # Check what's using the ports
   netstat -tulpn | grep :8000
   netstat -tulpn | grep :5432
   netstat -tulpn | grep :6379
   
   # Change ports in docker-compose.yml if needed
   ```

### Debug Mode

1. **Enable debug logging**:
   ```bash
   # In .env file
   DEBUG=true
   LOG_LEVEL=DEBUG
   ```

2. **Access container shell**:
   ```bash
   docker-compose exec auth-service bash
   
   # Or using Make
   make shell
   ```

3. **Database debugging**:
   ```bash
   # Access database shell
   make db-shell
   
   # Check tables
   \dt
   
   # Query users
   SELECT id, email, role, status FROM users;
   ```

## 🔧 Useful Commands

### Make Commands (if Make is available)

```bash
make help          # Show all available commands
make up            # Start all services
make down          # Stop all services
make logs          # View auth service logs
make shell         # Open shell in auth service
make test          # Run tests
make migrate       # Run database migrations
make backup        # Backup database
make clean         # Clean up everything
```

### Docker Commands

```bash
# View running containers
docker-compose ps

# Start specific service
docker-compose up postgres -d

# Scale auth service
docker-compose up --scale auth-service=3

# View resource usage
docker stats

# Clean up unused resources
docker system prune
```

### Database Commands

```bash
# Create new migration
docker-compose exec auth-service alembic revision --autogenerate -m "description"

# Upgrade to latest migration
docker-compose exec auth-service alembic upgrade head

# Downgrade to previous migration
docker-compose exec auth-service alembic downgrade -1

# View migration history
docker-compose exec auth-service alembic history
```

## 📋 Next Steps

After successful setup, you can:

1. **Integrate with Frontend**: Use the API endpoints in your React/Vue application
2. **Customize User Roles**: Modify the role system for your specific needs
3. **Add More OAuth Providers**: Implement Microsoft, Apple, GitHub OAuth
4. **Set Up Email Templates**: Customize email notifications
5. **Configure Alerts**: Set up monitoring alerts in Grafana
6. **Scale Services**: Add load balancing and multiple instances
7. **Implement 2FA**: Add two-factor authentication support

## 🆘 Getting Help

- **Documentation**: Check `/docs` endpoint when running
- **Logs**: Always check service logs first
- **Health Checks**: Use `/health` endpoint to verify service status
- **Monitoring**: Use Grafana dashboards for insights
- **Testing**: Use `/docs` interactive API documentation for testing

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
