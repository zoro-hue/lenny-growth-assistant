import logging
from typing import AsyncGenerator, Tuple
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
)
from .config import settings
from .errors import DatabaseConnectionError

logger = logging.getLogger(__name__)

# Global engine and sessionmaker references
_engine: AsyncEngine | None = None
_async_session_maker: async_sessionmaker[AsyncSession] | None = None
_active_db_url: str = ""


def get_engine() -> AsyncEngine:
    global _engine, _async_session_maker, _active_db_url
    if _engine is None:
        primary_url = settings.async_database_url
        try:
            # Create primary engine
            _engine = create_async_engine(
                primary_url,
                echo=False,
                pool_pre_ping=True,
                future=True,
            )
            _active_db_url = primary_url
            _async_session_maker = async_sessionmaker(
                _engine,
                expire_on_commit=False,
                class_=AsyncSession,
            )
            logger.info(f"Initialized primary database engine with URL: {primary_url}")
        except Exception as e:
            logger.warning(
                f"Failed to create primary database engine ({primary_url}): {e}. "
                f"Falling back to SQLite: {settings.sqlite_fallback_url}"
            )
            _engine = create_async_engine(
                settings.sqlite_fallback_url,
                echo=False,
                pool_pre_ping=True,
                future=True,
            )
            _active_db_url = settings.sqlite_fallback_url
            _async_session_maker = async_sessionmaker(
                _engine,
                expire_on_commit=False,
                class_=AsyncSession,
            )
    return _engine


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    get_engine()
    assert _async_session_maker is not None
    return _async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Dependency for request-scoped database sessions."""
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session rollback triggered due to: {e}")
            raise
        finally:
            await session.close()


async def check_database_health() -> Tuple[str, str]:
    """
    Validates database connectivity by executing SELECT 1.
    Returns (status, engine_dialect).
    status: 'connected' | 'disconnected' | 'error'
    """
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            val = result.scalar()
            if val == 1:
                return "connected", engine.dialect.name
            return "unexpected_result", engine.dialect.name
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        # If primary PostgreSQL failed and we haven't switched yet, switch to fallback
        if "sqlite" not in _active_db_url and settings.sqlite_fallback_url:
            logger.info(f"Switching database engine to fallback SQLite: {settings.sqlite_fallback_url}")
            switch_to_fallback()
            try:
                engine = get_engine()
                async with engine.connect() as conn:
                    result = await conn.execute(text("SELECT 1"))
                    if result.scalar() == 1:
                        return "connected", f"{engine.dialect.name} (fallback)"
            except Exception as e2:
                logger.error(f"Fallback database also failed: {e2}")
                return "error", str(e2)
        return "error", str(e)


def switch_to_fallback():
    """Switches the active engine to the local SQLite fallback."""
    global _engine, _async_session_maker, _active_db_url
    _active_db_url = settings.sqlite_fallback_url
    _engine = create_async_engine(
        settings.sqlite_fallback_url,
        echo=False,
        pool_pre_ping=True,
        future=True,
    )
    _async_session_maker = async_sessionmaker(
        _engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


async def init_models():
    """Create tables on startup if they don't already exist."""
    from .models.base import Base
    # Import all models so they register with Base.metadata
    from .models import session, message, artifact, transcript, user_metadata  # noqa: F401

    try:
        engine = get_engine()
        async with engine.begin() as conn:
            if engine.dialect.name == "postgresql":
                await conn.execute(text('CREATE EXTENSION IF NOT EXISTS vector;'))
                await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
            await conn.run_sync(Base.metadata.create_all)
            if engine.dialect.name == "postgresql":
                await conn.execute(text(
                    'CREATE INDEX IF NOT EXISTS ix_transcript_chunks_embedding ON transcript_chunks '
                    'USING hnsw (embedding vector_cosine_ops);'
                ))
        logger.info("Database tables verified/created successfully.")
    except Exception as e:
        logger.warning(f"Failed to auto-create tables on primary DB ({e}). Trying fallback SQLite...")
        switch_to_fallback()
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully on fallback SQLite.")
