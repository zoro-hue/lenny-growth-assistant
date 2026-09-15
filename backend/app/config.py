from typing import List, Union
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    port: int = Field(default=8000, alias="PORT")
    host: str = Field(default="0.0.0.0", alias="HOST")

    # Primary Database URL (asyncpg for PostgreSQL)
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/lenny_growth",
        alias="DATABASE_URL",
    )
    # Sync URL for Alembic (optional, auto-derived from DATABASE_URL if empty)
    database_sync_url: str = Field(
        default="",
        alias="DATABASE_SYNC_URL",
    )
    # Fallback SQLite DB URL when PostgreSQL daemon is offline
    sqlite_fallback_url: str = Field(
        default="sqlite+aiosqlite:///./lenny_growth.db",
        alias="SQLITE_FALLBACK_URL",
    )

    # CORS configuration as string or list
    cors_origins: Union[List[str], str] = Field(
        default="http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173",
        alias="CORS_ORIGINS",
    )

    # RAG & Embedding configuration
    embedding_provider: str = Field(default="auto", alias="EMBEDDING_PROVIDER")  # "auto" | "openai" | "ollama" | "mock"
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    # LLM & Agent configuration
    cloud_model: str = Field(default="gpt-4o-mini", alias="CLOUD_MODEL")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    openai_timeout: float = Field(default=30.0, alias="OPENAI_TIMEOUT")
    ollama_model: str = Field(default="llama3.2:3b", alias="OLLAMA_MODEL")
    ollama_timeout: float = Field(default=45.0, alias="OLLAMA_TIMEOUT")
    model_fallback_enabled: bool = Field(default=False, alias="MODEL_FALLBACK_ENABLED")
    agent_framework: str = Field(default="pi_coding_agent", alias="AGENT_FRAMEWORK")
    active_agent_framework: str = Field(default="pi_coding_agent", alias="ACTIVE_AGENT_FRAMEWORK")
    agent_max_iterations: int = Field(default=5, alias="AGENT_MAX_ITERATIONS")

    # Embedding & RAG configuration
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")
    embedding_dimensions: int = Field(default=1536, alias="EMBEDDING_DIMENSIONS")
    chunk_size: int = Field(default=800, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=150, alias="CHUNK_OVERLAP")
    retrieval_top_k: int = Field(default=3, alias="RETRIEVAL_TOP_K")
    similarity_threshold: float = Field(default=0.10, alias="SIMILARITY_THRESHOLD")
    transcripts_data_dir: str = Field(
        default=os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "transcripts"),
        alias="TRANSCRIPTS_DATA_DIR",
    )

    @property
    def is_production(self) -> bool:
        """Indicates whether running in a production deployment."""
        return self.app_env.strip().lower() in ("production", "prod")

    @property
    def effective_database_url(self) -> str:
        """
        Discovers database URL prioritizing explicit DATABASE_URL, Railway environment variables,
        and individual PG* connection components.
        """
        url = self.database_url.strip() if self.database_url else ""

        # If DATABASE_URL is unset or default localhost, check Railway / cloud env variables
        if not url or "localhost:5432" in url:
            for key in ("DATABASE_URL", "DATABASE_PRIVATE_URL", "DATABASE_PUBLIC_URL", "POSTGRES_URL", "DATABASE_URL_UNPOOLED"):
                val = os.getenv(key)
                if val and val.strip() and not ("localhost:5432" in val and self.is_production):
                    return val.strip()

            if os.getenv("PGHOST"):
                pghost = os.getenv("PGHOST", "").strip()
                pguser = os.getenv("PGUSER", "postgres").strip()
                pgpwd = os.getenv("PGPASSWORD", "").strip()
                pgport = os.getenv("PGPORT", "5432").strip()
                pgdb = os.getenv("PGDATABASE", "railway").strip()
                auth = f"{pguser}:{pgpwd}@" if pguser else ""
                return f"postgresql://{auth}{pghost}:{pgport}/{pgdb}"

        return url

    @property
    def async_database_url(self) -> str:
        """Returns PostgreSQL URL with asyncpg driver, normalizing Railway/Heroku postgres:// URLs and query params."""
        url = self.effective_database_url.strip()

        if self.is_production:
            if not url or "localhost:5432" in url:
                raise ValueError(
                    "APP_ENV is set to production, but DATABASE_URL is missing or set to localhost. "
                    "A valid PostgreSQL DATABASE_URL (e.g. from Railway PostgreSQL ${{Postgres.DATABASE_URL}}) is required."
                )

        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql+psycopg2://"):
            url = url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql+psycopg://"):
            url = url.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)

        # Normalize query params for asyncpg (e.g. sslmode -> ssl)
        if "sslmode=" in url:
            from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
            p = urlparse(url)
            qs = parse_qs(p.query)
            if "sslmode" in qs:
                mode = qs.pop("sslmode")[0]
                if mode in ("require", "verify-ca", "verify-full"):
                    qs["ssl"] = ["require"]
            new_query = urlencode(qs, doseq=True)
            url = urlunparse((p.scheme, p.netloc, p.path, p.params, new_query, p.fragment))

        return url

    @property
    def sync_database_url(self) -> str:
        """Returns synchronous database URL for Alembic migrations."""
        sync_url = self.database_sync_url.strip() if self.database_sync_url else ""
        # If explicit sync URL is unset or pointing to localhost while primary DB is remote, derive from primary DB
        if not sync_url or ("localhost:5432" in sync_url and "localhost:5432" not in self.effective_database_url):
            url = self.effective_database_url
        else:
            url = sync_url

        url = url.strip()

        if url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        elif url.startswith("postgresql+psycopg2://"):
            url = url.replace("postgresql+psycopg2://", "postgresql://", 1)
        elif url.startswith("postgresql+psycopg://"):
            url = url.replace("postgresql+psycopg://", "postgresql://", 1)
        elif url.startswith("sqlite+aiosqlite://"):
            url = url.replace("sqlite+aiosqlite://", "sqlite://", 1)
        return url

    @property
    def cors_origins_list(self) -> List[str]:
        if isinstance(self.cors_origins, str):
            return [i.strip() for i in self.cors_origins.split(",") if i.strip()]
        return list(self.cors_origins)

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
