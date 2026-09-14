import logging
from typing import Tuple, Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..schemas.chat import ChatRequest, ChatResponse
from ..schemas.message import MessageCreate, CitationSchema
from ..schemas.artifact import ArtifactCreate
from ..schemas.session import SessionUpdate
from .session_service import SessionService
from .message_service import MessageService
from .artifact_service import ArtifactService
from ..agent.providers import BaseLLMProvider

logger = logging.getLogger(__name__)


class ChatService:
    @staticmethod
    async def process_chat(
        db: AsyncSession,
        request: ChatRequest,
        custom_provider: Optional[BaseLLMProvider] = None,
    ) -> ChatResponse:
        # 1. Retrieve or auto-create session
        session = await SessionService.get_or_create_session(
            db, request.session_id, request.model_id
        )

        # 2. Determine model to use & update session model if provided
        model_id = request.model_id or session.active_model_id or "openai-cloud"
        if request.model_id and request.model_id != session.active_model_id:
            await SessionService.update_session(
                db, session.id, SessionUpdate(active_model_id=request.model_id)
            )

        # 3. Persist user message
        user_msg = await MessageService.create_message(
            db=db,
            session_id=session.id,
            data=MessageCreate(
                role="user",
                content=request.content.strip(),
                status="complete",
            ),
        )

        # 4. Auto-title session if it was "New conversation"
        await SessionService.auto_title_if_needed(db, session, request.content)

        lower_content = request.content.lower()
        is_essay = request.is_essay or "essay" in lower_content or "playbook" in lower_content or "ship 30" in lower_content

        # 5. Format query for agent execution
        query_text = request.content.strip()
        if request.is_essay and not ("essay" in lower_content or "playbook" in lower_content):
            query_text = f"Write an actionable Ship 30 for 30 playbook essay on: {query_text}"

        # 6. Retrieve recent conversation history for follow-up context
        all_prior = await MessageService.list_messages(db, session_id=session.id)
        # Exclude current user_msg from history list
        history_msgs = [m for m in all_prior if m.id != user_msg.id]
        history_dicts = [{"role": m.role, "content": m.content} for m in history_msgs]

        # 7. Execute Pi Coding Agent loop
        from ..agent.agent_service import AgentService, AgentExecutionResult
        agent_result: AgentExecutionResult = await AgentService.run(
            db=db,
            query=query_text,
            conversation_history=history_dicts,
            model_id=model_id,
            custom_provider=custom_provider,
        )

        # 8. If an essay artifact was generated, persist it
        artifact_resp = None
        artifact_id = None
        if agent_result.artifact_data:
            art_data = agent_result.artifact_data
            art = await ArtifactService.create_artifact(
                db=db,
                data=ArtifactCreate(
                    sessionId=session.id,
                    title=art_data.get("title") or f"Playbook: {request.content.strip()[:48]}",
                    type=art_data.get("type", "markdown"),
                    content=art_data.get("content", ""),
                    wordCount=art_data.get("word_count", len(art_data.get("content", "").split())),
                    sourceCount=art_data.get("source_count", len(agent_result.citations)),
                    allowScripts=art_data.get("allow_scripts", False),
                ),
            )
            artifact_resp = ArtifactService.to_response(art)
            artifact_id = art.id

        # 9. Persist assistant response based on agent outcome
        if agent_result.status == "error":
            assistant_msg = await MessageService.create_message(
                db=db,
                session_id=session.id,
                data=MessageCreate(
                    role="assistant",
                    content="",
                    status="error",
                    error_details=agent_result.error_details,
                ),
            )
        elif agent_result.status == "low-evidence":
            assistant_msg = await MessageService.create_message(
                db=db,
                session_id=session.id,
                data=MessageCreate(
                    role="assistant",
                    content=agent_result.content,
                    status="low-evidence",
                    citations=[],
                ),
            )
        else:
            assistant_msg = await MessageService.create_message(
                db=db,
                session_id=session.id,
                data=MessageCreate(
                    role="assistant",
                    content=agent_result.content,
                    status="complete",
                    citations=agent_result.citations,
                    artifact_id=artifact_id,
                ),
            )

        return ChatResponse(
            sessionId=session.id,
            userMessage=MessageService.to_response(user_msg),
            assistantMessage=MessageService.to_response(assistant_msg),
            artifact=artifact_resp,
        )

