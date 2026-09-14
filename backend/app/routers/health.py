from fastapi import APIRouter
from ..database import check_database_health
from ..schemas.common import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def get_health():
    """
    Health check endpoint verifying system responsiveness and live database connectivity.
    """
    db_status, dialect = await check_database_health()
    return HealthResponse(
        status="ok",
        database=db_status,
        db_dialect=dialect,
        version="1.0.0",
    )
