#!/bin/bash

# BillFusion Auth Service startup script

set -e

echo "🚀 Starting BillFusion Auth Service..."

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
python -c "
import asyncio
import sys
from app.core.database import check_database_connection

async def wait_for_db():
    max_retries = 30
    retry_count = 0
    while retry_count < max_retries:
        try:
            if await check_database_connection():
                print('✅ Database connection successful')
                return
        except Exception as e:
            print(f'❌ Database connection failed: {e}')
        retry_count += 1
        if retry_count < max_retries:
            print(f'🔄 Retrying database connection ({retry_count}/{max_retries})...')
            await asyncio.sleep(2)
    
    print('❌ Failed to connect to database after maximum retries')
    sys.exit(1)

asyncio.run(wait_for_db())
"

# Run database migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Create initial admin user if it doesn't exist
echo "👤 Creating initial admin user..."
python -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole, UserStatus, AuthProvider
from app.services.auth_service import AuthService
from sqlalchemy import select
import os

async def create_admin_user():
    async with AsyncSessionLocal() as session:
        # Check if admin user exists
        stmt = select(User).where(User.role == UserRole.ADMIN)
        result = await session.execute(stmt)
        admin_user = result.scalar_one_or_none()
        
        if not admin_user:
            auth_service = AuthService(session)
            admin_user = await auth_service.register_user(
                email=os.getenv('ADMIN_EMAIL', 'admin@billfusion.com'),
                password=os.getenv('ADMIN_PASSWORD', 'AdminPassword123!'),
                first_name='System',
                last_name='Administrator',
                role=UserRole.ADMIN
            )
            admin_user.status = UserStatus.ACTIVE
            admin_user.is_email_verified = True
            await session.commit()
            print('✅ Admin user created successfully')
        else:
            print('ℹ️  Admin user already exists')

try:
    asyncio.run(create_admin_user())
except Exception as e:
    print(f'⚠️  Failed to create admin user: {e}')
"

# Start the application
echo "🌟 Starting FastAPI application..."

if [ "$ENVIRONMENT" = "development" ]; then
    echo "🔧 Running in development mode with auto-reload"
    exec uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload \
        --log-config logging.json
else
    echo "🏭 Running in production mode"
    exec gunicorn app.main:app \
        --bind 0.0.0.0:8000 \
        --worker-class uvicorn.workers.UvicornWorker \
        --workers ${WORKERS:-4} \
        --worker-connections ${WORKER_CONNECTIONS:-1000} \
        --max-requests ${MAX_REQUESTS:-1000} \
        --max-requests-jitter ${MAX_REQUESTS_JITTER:-50} \
        --timeout ${TIMEOUT:-120} \
        --keepalive ${KEEPALIVE:-5} \
        --log-level ${LOG_LEVEL:-info} \
        --access-logfile - \
        --error-logfile -
fi
