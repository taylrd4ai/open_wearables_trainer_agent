"""Open Wearables Personal Trainer - Database configuration."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, AsyncIterator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENV == "development",
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base declarative class for all models."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    """
    Async context manager version of get_db(), for use outside FastAPI's
    request/dependency cycle -- e.g. from the Telegram bot, or from a
    scheduled reminder job. Same commit/rollback/close semantics as get_db().
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def _seed_exercises_if_empty() -> None:
    """Populates the exercises table from the seed list on first run."""
    from app.models.exercise import Exercise
    from app.models.exercise_seed import EXERCISE_SEED

    async with get_session() as session:
        result = await session.execute(select(Exercise.id).limit(1))
        if result.first() is not None:
            return  # already seeded

        for row in EXERCISE_SEED:
            session.add(Exercise(**row))


async def init_db() -> None:
    """Initialize database tables (for development/testing)."""
    # Ensure all models are imported so they register on Base.metadata
    # before create_all() runs.
    from app.models.user import User  # noqa: F401
    from app.models.workout_session import WorkoutSession  # noqa: F401
    from app.models.exercise_entry import ExerciseEntry  # noqa: F401
    from app.models.exercise import Exercise  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await _seed_exercises_if_empty()
