-- Initialize database for BillFusion Auth Service
-- This script is run when the database container starts

-- Set timezone
SET timezone = 'UTC';

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create database if it doesn't exist
-- (This is typically handled by the POSTGRES_DB environment variable)

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE billfusion_auth TO postgres;

-- Create indexes for performance (these will be created by migrations, but good to have as backup)
-- Note: These are created here as a fallback; the actual indexes should be created via Alembic migrations

-- TODO: Add database-specific configurations
-- TODO: Add performance tuning parameters
-- TODO: Add security configurations
-- TODO: Add backup configurations

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'BillFusion Auth Database initialized successfully at %', NOW();
END
$$;
