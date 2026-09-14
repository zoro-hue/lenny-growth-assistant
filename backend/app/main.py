import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from .config import settings
from .database import init_models, check_database_health
from .errors import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler,
)
from .routers import (
    health_router,
    sessions_router,
    chat_router,
    artifacts_router,
    knowledge_router,
    models_router,
)

logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("lenny_backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting The Lenny Growth Assistant Backend...")
    # Initialize database models / verify tables
    await init_models()
    db_status, dialect = await check_database_health()
    logger.info(f"Database health: {db_status} (dialect: {dialect})")
    yield
    logger.info("Shutting down The Lenny Growth Assistant Backend...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="The Lenny Growth Assistant API",
        description="Grounded research instrument for product and growth professionals backed by Lenny's Podcast transcripts.",
        version="1.0.0",
        lifespan=lifespan,
    )

    # 1. CORS Configuration per Requirement 11
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Structured API Error Handlers per Requirement 9 & 10
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # 3. Mount Routers per Requirement 2
    app.include_router(health_router)
    app.include_router(sessions_router)
    app.include_router(chat_router)
    app.include_router(artifacts_router)
    app.include_router(knowledge_router)
    app.include_router(models_router)

    return app


app = create_app()
