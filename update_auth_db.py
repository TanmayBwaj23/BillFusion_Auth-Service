import asyncio
from sqlalchemy import text
from app.core.database import engine

async def add_employee_id_field():
    print("Connecting to database...")
    try:
        async with engine.begin() as conn:
            print("Adding employee_id column...")
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS employee_id VARCHAR(50)"))
            
            print("Creating index...")
            await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_employee_id ON users(employee_id)"))
            
            print("Updating test user...")
            await conn.execute(text("UPDATE users SET employee_id = 'EMP001' WHERE email = 'logintest@test.com'"))
            
            print("Checking for other test users...")
            # Update or create other test users if they exist/don't exist
            # For now just ensuring EMP001 is linked
            
        print("✅ Database updated successfully!")
    except Exception as e:
        print(f"❌ Error updating database: {e}")

if __name__ == "__main__":
    asyncio.run(add_employee_id_field())
