from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.message import MessageModel
from ..schemas.message import MessageCreate, MessageResponse, CitationSchema
from .session_service import SessionService


class MessageService:
    @staticmethod
    async def create_message(
        db: AsyncSession,
        session_id: str,
        data: MessageCreate,
    ) -> MessageModel:
        # Validate session existence
        session = await SessionService.get_session(db, session_id)

        citations_data = [
            c.model_dump(by_alias=True) for c in (data.citations or [])
        ]

        message = MessageModel(
            session_id=session_id,
            role=data.role,
            content=data.content,
            status=data.status or "complete",
            citations=citations_data,
            artifact_id=data.artifact_id,
            error_details=data.error_details,
        )
        db.add(message)

        # Update session updated_at
        from datetime import datetime, timezone
        session.updated_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(message)
        return message

    @staticmethod
    async def list_messages(
        db: AsyncSession,
        session_id: str,
    ) -> List[MessageModel]:
        # Validate session existence
        await SessionService.get_session(db, session_id)

        stmt = (
            select(MessageModel)
            .where(MessageModel.session_id == session_id)
            .order_by(MessageModel.created_at.asc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    def to_response(message: MessageModel) -> MessageResponse:
        citations = []
        for c in (message.citations or []):
            try:
                citations.append(CitationSchema(**c))
            except Exception:
                pass

        time_str = message.created_at.strftime("%H:%M")

        return MessageResponse(
            id=message.id,
            role=message.role,
            content=message.content,
            status=message.status,
            timestamp=time_str,
            createdAt=message.created_at,
            citations=citations,
            artifactId=message.artifact_id,
            errorDetails=message.error_details,
        )
