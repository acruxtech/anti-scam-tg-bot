from typing import AsyncGenerator

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER

connection_string = URL.create(
  'postgresql+asyncpg',
  username=DB_USER,
  password=DB_PASS,
  host=DB_HOST,
  database=DB_NAME,
  port=DB_PORT
)

Base = declarative_base()

engine = create_async_engine(connection_string)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
