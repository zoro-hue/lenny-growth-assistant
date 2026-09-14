from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime


class CitationSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    episode_number: Optional[int] = Field(default=None, alias="episodeNumber")
    episode_title: str = Field(alias="episodeTitle")
    guest: str
    guest_role: Optional[str] = Field(default=None, alias="guestRole")
    timestamp: str
    quote_excerpt: str = Field(alias="quoteExcerpt")
    episode_url: str = Field(alias="episodeUrl")
    relevance_score: Optional[float] = Field(default=None, alias="relevanceScore")


class MessageCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    role: str = Field(..., description="'user' | 'assistant' | 'system'")
    status: Optional[str] = Field(default="complete")
    content: str = Field(default="")
    citations: Optional[List[CitationSchema]] = Field(default_factory=list)
    artifact_id: Optional[str] = Field(default=None, alias="artifactId")
    error_details: Optional[Dict[str, Any]] = Field(default=None, alias="errorDetails")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str, info: Any) -> str:
        status_val = info.data.get("status") if hasattr(info, "data") else None
        if status_val == "error":
            return v
        if not v or not v.strip():
            raise ValueError("content must not be empty")
        return v


MessageCreate.model_rebuild()


class MessageResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: str
    role: str
    content: str
    status: str
    timestamp: str
    created_at: datetime = Field(alias="createdAt")
    citations: List[CitationSchema] = Field(default_factory=list)
    artifact_id: Optional[str] = Field(default=None, alias="artifactId")
    error_details: Optional[Dict[str, Any]] = Field(default=None, alias="errorDetails")
