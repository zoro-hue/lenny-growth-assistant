import os
import pytest
from app.config import Settings
from app.database import mask_db_url, switch_to_fallback
from app.errors import DatabaseConnectionError


def test_mask_db_url_hides_password():
    url = "postgresql+asyncpg://postgres:supersecretpassword@roundhouse.proxy.rlwy.net:12345/railway"
    masked = mask_db_url(url)
    assert "supersecretpassword" not in masked
    assert "postgres" in masked
    assert "roundhouse.proxy.rlwy.net" in masked
    assert "***" in masked


def test_async_database_url_normalization_postgres_scheme():
    s = Settings(
        APP_ENV="development",
        DATABASE_URL="postgres://user:pass@host.internal:5432/db",
    )
    assert s.async_database_url.startswith("postgresql+asyncpg://user:pass@host.internal:5432/db")


def test_async_database_url_normalization_postgresql_scheme():
    s = Settings(
        APP_ENV="development",
        DATABASE_URL="postgresql://user:pass@host.internal:5432/db",
    )
    assert s.async_database_url.startswith("postgresql+asyncpg://user:pass@host.internal:5432/db")


def test_async_database_url_normalization_sslmode():
    s = Settings(
        APP_ENV="development",
        DATABASE_URL="postgresql://user:pass@host.internal:5432/db?sslmode=require",
    )
    assert "ssl=require" in s.async_database_url
    assert "sslmode" not in s.async_database_url


def test_sync_database_url_uses_postgresql_scheme():
    s = Settings(
        APP_ENV="development",
        DATABASE_URL="postgres://user:pass@host.internal:5432/db",
    )
    assert s.sync_database_url.startswith("postgresql://user:pass@host.internal:5432/db")


def test_railway_database_private_url_fallback(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DATABASE_PRIVATE_URL", "postgresql://user:pass@postgres.railway.internal:5432/railway")
    s = Settings(
        APP_ENV="development",
        DATABASE_URL="",
    )
    assert "postgres.railway.internal" in s.async_database_url


def test_railway_database_public_url_fallback(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_PRIVATE_URL", raising=False)
    monkeypatch.setenv("DATABASE_PUBLIC_URL", "postgresql://user:pass@roundhouse.proxy.rlwy.net:12345/railway")
    s = Settings(
        APP_ENV="development",
        DATABASE_URL="",
    )
    assert "roundhouse.proxy.rlwy.net" in s.async_database_url


def test_railway_pghost_construction(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_PRIVATE_URL", raising=False)
    monkeypatch.delenv("DATABASE_PUBLIC_URL", raising=False)
    monkeypatch.delenv("POSTGRES_URL", raising=False)
    monkeypatch.setenv("PGHOST", "postgres.railway.internal")
    monkeypatch.setenv("PGPORT", "5432")
    monkeypatch.setenv("PGUSER", "postgres")
    monkeypatch.setenv("PGPASSWORD", "secret")
    monkeypatch.setenv("PGDATABASE", "railway")

    s = Settings(
        APP_ENV="development",
        DATABASE_URL="",
    )
    assert "postgres.railway.internal" in s.async_database_url


def test_production_fails_when_database_url_missing(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_PRIVATE_URL", raising=False)
    monkeypatch.delenv("DATABASE_PUBLIC_URL", raising=False)
    monkeypatch.delenv("POSTGRES_URL", raising=False)
    monkeypatch.delenv("PGHOST", raising=False)

    s = Settings(
        APP_ENV="production",
        DATABASE_URL="",
    )
    with pytest.raises(ValueError, match="APP_ENV is set to production"):
        _ = s.async_database_url


def test_production_fails_when_database_url_points_to_localhost(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_PRIVATE_URL", raising=False)
    monkeypatch.delenv("DATABASE_PUBLIC_URL", raising=False)
    monkeypatch.delenv("POSTGRES_URL", raising=False)
    monkeypatch.delenv("PGHOST", raising=False)

    s = Settings(
        APP_ENV="production",
        DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/lenny_growth",
    )
    with pytest.raises(ValueError, match="APP_ENV is set to production"):
        _ = s.async_database_url


def test_production_blocks_switch_to_fallback(monkeypatch):
    from app.config import settings
    orig_env = settings.app_env
    try:
        settings.app_env = "production"
        with pytest.raises(DatabaseConnectionError, match="Production MUST use Railway PostgreSQL"):
            switch_to_fallback()
    finally:
        settings.app_env = orig_env
