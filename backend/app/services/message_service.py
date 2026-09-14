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

        # Compute evidence strength indicator
        evidence_strength = None
        evidence_label = None
        if message.role == "assistant":
            if message.status == "low-evidence" or (not citations and message.status != "error"):
                evidence_strength = "not-grounded"
                evidence_label = "No supporting Lenny Podcast evidence found"
            elif len(citations) == 1:
                evidence_strength = "limited"
                evidence_label = "1 relevant transcript source"
            elif len(citations) >= 2:
                unique_speakers = len(set(c.guest for c in citations if c.guest))
                speaker_str = f"{unique_speakers} speakers" if unique_speakers > 1 else "1 speaker"
                evidence_strength = "high"
                evidence_label = f"{len(citations)} transcript sources · {speaker_str}"

        # Contextual deterministic follow-up suggestions
        follow_up_suggestions = []
        if message.role == "assistant" and message.status == "complete":
            primary_guests = [c.guest.lower() for c in citations if c.guest]
            content_lower = message.content.lower()

            if any("balfour" in g for g in primary_guests) or "balfour" in content_lower:
                follow_up_suggestions = [
                    "Compare Brian Balfour and Elena Verna on growth loops",
                    "What metric should I track for Channel-Model Fit?",
                    "Turn this into a playbook",
                    "Write a Ship 30/30 essay",
                ]
            elif any("winters" in g for g in primary_guests) or "winters" in content_lower:
                follow_up_suggestions = [
                    "Compare Casey Winters and Brian Balfour on retention",
                    "How does this apply to PLG?",
                    "Turn this into a playbook",
                    "Write a Ship 30/30 essay",
                ]
            elif any("verna" in g for g in primary_guests) or "verna" in content_lower:
                follow_up_suggestions = [
                    "Compare Elena Verna and Brian Balfour on PLG",
                    "What is the Time-to-Aha threshold for B2B activation?",
                    "Turn this into a playbook",
                    "Write a Ship 30/30 essay",
                ]
            elif any("vohra" in g for g in primary_guests) or "vohra" in content_lower:
                follow_up_suggestions = [
                    "Compare Rahul Vohra and Casey Winters on PMF signals",
                    "How do I filter the 40% PMF survey respondents?",
                    "Turn this into a playbook",
                    "Write a Ship 30/30 essay",
                ]
            elif any("doshi" in g for g in primary_guests) or "doshi" in content_lower:
                follow_up_suggestions = [
                    "Compare Shreyas Doshi and Brian Balfour on high agency",
                    "How does the LNO framework apply to roadmap decisions?",
                    "Turn this into a playbook",
                    "Write a Ship 30/30 essay",
                ]
            elif "compare perspectives" in content_lower:
                follow_up_suggestions = [
                    "What metric should I track?",
                    "How does this apply to PLG?",
                    "Turn this into a playbook",
                    "Write a Ship 30/30 essay",
                ]
            elif message.artifact_id:
                follow_up_suggestions = [
                    "How do I implement this framework step-by-step?",
                    "What metric should I track?",
                    "Compare this with Elena Verna's view",
                    "Write a Ship 30/30 essay",
                ]
            else:
                follow_up_suggestions = [
                    "How does this apply to PLG?",
                    "What metric should I track?",
                    "Compare this with Elena Verna's view",
                    "Turn this into a playbook",
                ]

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
            evidenceStrength=evidence_strength,
            evidenceLabel=evidence_label,
            followUpSuggestions=follow_up_suggestions,
        )
