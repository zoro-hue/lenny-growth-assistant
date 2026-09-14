from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from .message import MessageResponse
from .artifact import ArtifactResponse


class ChatRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    session_id: str = Field(alias="sessionId")
    content: str = Field(..., min_length=1)
    model_id: Optional[str] = Field(default="openai-cloud", alias="modelId")
    is_essay: Optional[bool] = Field(default=False, alias="isEssay")


class ChatResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    session_id: str = Field(alias="sessionId")
    user_message: MessageResponse = Field(alias="userMessage")
    assistant_message: MessageResponse = Field(alias="assistantMessage")
    artifact: Optional[ArtifactResponse] = None
