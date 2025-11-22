#!/bin/bash
# Production startup script for Render

set -e  # Exit on any error

echo "🚀 Starting BillFusion Auth Service..."

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
until python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')" 2>/dev/null; do
  echo "Database not ready, waiting..."
  sleep 2
done
echo "✅ Database connected!"

# Wait for Redis to be ready
echo "⏳ Waiting for Redis connection..."
until python -c "import redis; redis.from_url('$REDIS_URL').ping()" 2>/dev/null; do
  echo "Redis not ready, waiting..."
  sleep 2
done
echo "✅ Redis connected!"

# Run database migrations
echo "📊 Running database migrations..."
python -m alembic upgrade head
echo "✅ Migrations completed!"

# Create initial admin user if needed
echo "👤 Setting up initial users..."
python -c "
import asyncio
from app.core.database import get_db_session
from app.services.auth_service import AuthService
from app.models.user import User
from sqlalchemy import select
import os

async def create_admin():
    async with get_db_session() as db:
        auth_service = AuthService(db)
        
        # Check if admin exists
        stmt = select(User).where(User.email == 'admin@billfusion.com')
        result = await db.execute(stmt)
        admin = result.scalar_one_or_none()
        
        if not admin:
            print('Creating initial admin user...')
            admin = await auth_service.register_user(
                email='admin@billfusion.com',
                password=os.getenv('ADMIN_PASSWORD', 'Admin123!'),
                first_name='System',
                last_name='Administrator',
                role='ADMIN'
            )
            admin.status = 'ACTIVE'
            admin.is_email_verified = True
            await db.commit()
            print('✅ Admin user created!')
        else:
            print('✅ Admin user already exists')

if __name__ == '__main__':
    asyncio.run(create_admin())
"

# Start the application
echo "🎯 Starting FastAPI server..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers ${WEB_CONCURRENCY:-1} \
    --log-level info \
    --access-log \
    --no-use-colors
