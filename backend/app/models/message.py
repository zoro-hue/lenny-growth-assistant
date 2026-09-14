import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin


class MessageModel(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: f"msg-{uuid.uuid4().hex[:12]}",
    )
    session_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        String(32),
        nullable=False,  # 'user' | 'assistant' | 'system'
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="complete",  # 'complete' | 'streaming' | 'low-evidence' | 'error'
        nullable=False,
    )
    citations: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    artifact_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )
    error_details: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    # Relationship back to session
    session: Mapped["SessionModel"] = relationship(
        "SessionModel",
        back_populates="messages",
    )
