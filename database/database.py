from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os

# Load environment variables (Replace with actual credentials or use dotenv)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://chat_db_2vzj_user:D9TDySt9yocqhZokB14HDMFMaGzrDZTD@dpg-cv5qpljtq21c73db3vkg-a/chat_db_2vzj")

# Create an async engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Create a session factory
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Dependency to get the session
async def get_db():
    async with SessionLocal() as session:
        yield session
