from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from src.config import DATABASE_URL

if not DATABASE_URL:
    raise ValueError("Database URL is not set check the .env file")

engine = create_async_engine(DATABASE_URL, poolclass=NullPool)


async_session_maker = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


class Base(AsyncAttrs, DeclarativeBase):
    pass


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_maker() as session:
        yield session
