from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class HealthResponse(BaseModel):
    status: str = Field(default="ok", description="Overall service status")
    database: str = Field(default="connected", description="Database connectivity status")
    db_dialect: str = Field(default="postgresql", description="Active database engine dialect")
    version: str = Field(default="1.0.0", description="API version")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
