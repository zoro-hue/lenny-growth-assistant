from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from .message import MessageResponse
from .artifact import ArtifactResponse


class SessionCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: Optional[str] = Field(default="New conversation")
    active_model_id: Optional[str] = Field(default="openai-cloud", alias="activeModelId")


class SessionUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: Optional[str] = None
    active_model_id: Optional[str] = Field(default=None, alias="activeModelId")


class SessionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: str
    title: str
    active_model_id: str = Field(alias="activeModelId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    message_count: int = Field(default=0, alias="messageCount")
    artifact_ids: List[str] = Field(default_factory=list, alias="artifactIds")


class SessionDetailResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: str
    title: str
    active_model_id: str = Field(alias="activeModelId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    messages: List[MessageResponse] = Field(default_factory=list)
    artifacts: List[ArtifactResponse] = Field(default_factory=list)
    artifact_ids: List[str] = Field(default_factory=list, alias="artifactIds")
