from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.artifact import ArtifactModel
from ..schemas.artifact import ArtifactCreate, ArtifactUpdate, ArtifactResponse
from ..errors import EntityNotFoundError
from .session_service import SessionService


class ArtifactService:
    @staticmethod
    async def create_artifact(db: AsyncSession, data: ArtifactCreate) -> ArtifactModel:
        # Validate session existence
        await SessionService.get_session(db, data.session_id)

        word_count = len(data.content.split()) if not data.word_count else data.word_count

        artifact = ArtifactModel(
            session_id=data.session_id,
            title=data.title,
            type=data.type,
            content=data.content,
            word_count=word_count,
            source_count=data.source_count or 0,
            allow_scripts=data.allow_scripts or False,
        )
        db.add(artifact)
        await db.commit()
        await db.refresh(artifact)
        return artifact

    @staticmethod
    async def get_artifact(db: AsyncSession, artifact_id: str) -> ArtifactModel:
        stmt = select(ArtifactModel).where(ArtifactModel.id == artifact_id)
        result = await db.execute(stmt)
        artifact = result.scalar_one_or_none()
        if not artifact:
            raise EntityNotFoundError("Artifact", artifact_id)
        return artifact

    @staticmethod
    async def list_artifacts(db: AsyncSession, session_id: Optional[str] = None) -> List[ArtifactModel]:
        stmt = select(ArtifactModel).order_by(desc(ArtifactModel.created_at))
        if session_id:
            stmt = stmt.where(ArtifactModel.session_id == session_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update_artifact(db: AsyncSession, artifact_id: str, data: ArtifactUpdate) -> ArtifactModel:
        artifact = await ArtifactService.get_artifact(db, artifact_id)
        if data.title is not None:
            artifact.title = data.title.strip()
        if data.content is not None:
            artifact.content = data.content
            artifact.word_count = len(data.content.split())
        if data.allow_scripts is not None:
            artifact.allow_scripts = data.allow_scripts
        await db.commit()
        await db.refresh(artifact)
        return artifact

    @staticmethod
    def to_response(artifact: ArtifactModel) -> ArtifactResponse:
        return ArtifactResponse(
            id=artifact.id,
            sessionId=artifact.session_id,
            title=artifact.title,
            type=artifact.type,
            content=artifact.content,
            wordCount=artifact.word_count,
            sourceCount=artifact.source_count,
            allowScripts=artifact.allow_scripts,
            createdAt=artifact.created_at,
            updatedAt=artifact.updated_at,
        )
