import asyncio
from database.database import engine
from models.models import Base

# Function to create tables
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created successfully!")

# Run the function
if __name__ == "__main__":
    asyncio.run(create_tables())
