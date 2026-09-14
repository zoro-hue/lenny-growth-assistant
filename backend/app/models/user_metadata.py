import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin


class UserMetadataModel(Base, TimestampMixin):
    __tablename__ = "user_metadata"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: f"user-{uuid.uuid4().hex[:12]}",
    )
    user_identifier: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        index=True,
        nullable=False,
        default="default-growth-researcher",
    )
    preferences: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        default=lambda: {
            "preferred_model": "openai-cloud",
            "citation_view": "inline",
            "theme": "editorial-paper",
        },
        nullable=False,
    )

    # Relationships
    sessions: Mapped[List["SessionModel"]] = relationship(
        "SessionModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )
