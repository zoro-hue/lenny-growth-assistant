from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..schemas.artifact import ArtifactCreate, ArtifactUpdate, ArtifactResponse
from ..services.artifact_service import ArtifactService

router = APIRouter(prefix="/api/artifacts", tags=["Artifacts"])


@router.get("", response_model=List[ArtifactResponse])
async def list_artifacts(
    session_id: Optional[str] = Query(None, alias="sessionId"),
    db: AsyncSession = Depends(get_db),
):
    """List all artifacts, optionally filtered by session."""
    artifacts = await ArtifactService.list_artifacts(db, session_id)
    return [ArtifactService.to_response(a) for a in artifacts]


@router.post("", response_model=ArtifactResponse, status_code=status.HTTP_201_CREATED)
async def create_artifact(
    data: ArtifactCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new artifact associated with a session."""
    artifact = await ArtifactService.create_artifact(db, data)
    return ArtifactService.to_response(artifact)


@router.get("/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(
    artifact_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve details and content of a generated artifact."""
    artifact = await ArtifactService.get_artifact(db, artifact_id)
    return ArtifactService.to_response(artifact)


@router.patch("/{artifact_id}", response_model=ArtifactResponse)
async def update_artifact(
    artifact_id: str,
    data: ArtifactUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update artifact title, content, or script execution permissions."""
    artifact = await ArtifactService.update_artifact(db, artifact_id, data)
    return ArtifactService.to_response(artifact)
