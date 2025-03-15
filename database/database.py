from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# Load environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL is not set! Make sure to set it in the environment.")

# Create an async engine
engine = create_async_engine(DATABASE_URL, echo=True, connect_args={"ssl": None})

# Create a session factory
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Define Base for models
Base = declarative_base()

# Dependency to get the session
async def get_db():
    async with SessionLocal() as session:
        yield session
