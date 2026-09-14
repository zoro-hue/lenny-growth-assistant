from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas.session import (
    SessionCreate,
    SessionUpdate,
    SessionResponse,
    SessionDetailResponse,
)
from ..schemas.message import MessageCreate, MessageResponse
from ..services.session_service import SessionService
from ..services.message_service import MessageService
from ..services.artifact_service import ArtifactService

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


@router.get("", response_model=List[SessionResponse])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    """Retrieve all conversation sessions ordered by most recently updated."""
    sessions = await SessionService.list_sessions(db)
    response = []
    for s in sessions:
        response.append(
            SessionResponse(
                id=s.id,
                title=s.title,
                activeModelId=s.active_model_id,
                createdAt=s.created_at,
                updatedAt=s.updated_at,
                messageCount=len(s.messages),
                artifactIds=[a.id for a in s.artifacts],
            )
        )
    return response


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(data: SessionCreate, db: AsyncSession = Depends(get_db)):
    """Create a new independent conversation session."""
    session = await SessionService.create_session(db, data)
    return SessionResponse(
        id=session.id,
        title=session.title,
        activeModelId=session.active_model_id,
        createdAt=session.created_at,
        updatedAt=session.updated_at,
        messageCount=0,
        artifactIds=[],
    )


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve full details of a session including messages and artifacts."""
    session = await SessionService.get_session(db, session_id)
    messages = await MessageService.list_messages(db, session_id)
    artifacts = await ArtifactService.list_artifacts(db, session_id)
    return SessionDetailResponse(
        id=session.id,
        title=session.title,
        activeModelId=session.active_model_id,
        createdAt=session.created_at,
        updatedAt=session.updated_at,
        messages=[MessageService.to_response(m) for m in messages],
        artifacts=[ArtifactService.to_response(a) for a in artifacts],
        artifactIds=[a.id for a in artifacts],
    )


@router.patch("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    data: SessionUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Rename a session or switch its active model."""
    session = await SessionService.update_session(db, session_id, data)
    return SessionResponse(
        id=session.id,
        title=session.title,
        activeModelId=session.active_model_id,
        createdAt=session.created_at,
        updatedAt=session.updated_at,
        messageCount=len(session.messages),
        artifactIds=[a.id for a in session.artifacts],
    )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a session and all its associated messages and artifacts."""
    await SessionService.delete_session(db, session_id)
    return None


@router.get("/{session_id}/messages", response_model=List[MessageResponse])
async def list_session_messages(session_id: str, db: AsyncSession = Depends(get_db)):
    """List all messages in chronological order for a specific session."""
    messages = await MessageService.list_messages(db, session_id)
    return [MessageService.to_response(m) for m in messages]


@router.post(
    "/{session_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_session_message(
    session_id: str,
    data: MessageCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a message to a session's conversation history."""
    message = await MessageService.create_message(db, session_id, data)
    return MessageService.to_response(message)


@router.post("/seed-demo", status_code=status.HTTP_200_OK)
async def seed_demo_endpoint(
    reset: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """Seed clean, professional demo conversations into the session history."""
    from ..scripts.seed_demo import seed_demo_conversations
    result = await seed_demo_conversations(db, reset=reset)
    return result
