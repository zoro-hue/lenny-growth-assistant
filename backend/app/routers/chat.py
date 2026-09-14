from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..schemas.chat import ChatRequest, ChatResponse
from ..services.chat_service import ChatService

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_interaction(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Process a chat message in a session: persists user prompt, generates
    grounded response with transcript citations or essay playbook, and persists assistant reply.
    """
    return await ChatService.process_chat(db, request)
