from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class ArtifactCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    session_id: str = Field(alias="sessionId")
    title: str = Field(..., min_length=1)
    type: str = Field(default="markdown", description="'markdown' | 'html'")
    content: str = Field(default="")
    word_count: Optional[int] = Field(default=0, alias="wordCount")
    source_count: Optional[int] = Field(default=0, alias="sourceCount")
    allow_scripts: Optional[bool] = Field(default=False, alias="allowScripts")


class ArtifactUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: Optional[str] = None
    content: Optional[str] = None
    allow_scripts: Optional[bool] = Field(default=None, alias="allowScripts")


class ArtifactResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: str
    session_id: str = Field(alias="sessionId")
    title: str
    type: str
    content: str
    word_count: int = Field(alias="wordCount")
    source_count: int = Field(alias="sourceCount")
    allow_scripts: bool = Field(alias="allowScripts")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
