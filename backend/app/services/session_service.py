from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.session import SessionModel
from ..models.message import MessageModel
from ..models.artifact import ArtifactModel
from ..schemas.session import SessionCreate, SessionUpdate
from ..errors import EntityNotFoundError


class SessionService:
    @staticmethod
    async def create_session(db: AsyncSession, data: SessionCreate) -> SessionModel:
        session = SessionModel(
            title=data.title or "New conversation",
            active_model_id=data.active_model_id or "openai-cloud",
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def list_sessions(db: AsyncSession) -> List[SessionModel]:
        stmt = (
            select(SessionModel)
            .options(
                selectinload(SessionModel.messages),
                selectinload(SessionModel.artifacts),
            )
            .order_by(desc(SessionModel.updated_at))
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_session(db: AsyncSession, session_id: str) -> SessionModel:
        stmt = (
            select(SessionModel)
            .where(SessionModel.id == session_id)
            .options(
                selectinload(SessionModel.messages),
                selectinload(SessionModel.artifacts),
            )
        )
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
        if not session:
            raise EntityNotFoundError("Session", session_id)
        return session

    @staticmethod
    async def get_or_create_session(
        db: AsyncSession,
        session_id: str,
        active_model_id: Optional[str] = "openai-cloud",
    ) -> SessionModel:
        stmt = (
            select(SessionModel)
            .where(SessionModel.id == session_id)
            .options(
                selectinload(SessionModel.messages),
                selectinload(SessionModel.artifacts),
            )
        )
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
        if not session:
            session = SessionModel(
                id=session_id,
                title="New conversation",
                active_model_id=active_model_id or "openai-cloud",
            )
            db.add(session)
            await db.commit()
            # Reload with relationships
            stmt_new = (
                select(SessionModel)
                .where(SessionModel.id == session_id)
                .options(
                    selectinload(SessionModel.messages),
                    selectinload(SessionModel.artifacts),
                )
            )
            res_new = await db.execute(stmt_new)
            session = res_new.scalar_one()
        return session

    @staticmethod
    async def update_session(db: AsyncSession, session_id: str, data: SessionUpdate) -> SessionModel:
        session = await SessionService.get_session(db, session_id)
        if data.title is not None:
            session.title = data.title.strip() or "Untitled"
        if data.active_model_id is not None:
            session.active_model_id = data.active_model_id
        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def delete_session(db: AsyncSession, session_id: str) -> bool:
        session = await SessionService.get_session(db, session_id)
        await db.delete(session)
        await db.commit()
        return True

    @staticmethod
    async def auto_title_if_needed(db: AsyncSession, session: SessionModel, first_message_text: str) -> None:
        if session.title == "New conversation" and first_message_text.strip():
            words = first_message_text.strip().split()[:6]
            session.title = " ".join(words)
            await db.commit()
            await db.refresh(session)
