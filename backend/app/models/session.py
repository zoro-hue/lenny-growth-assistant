import uuid
from typing import List, Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin


class SessionModel(Base, TimestampMixin):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: f"session-{uuid.uuid4().hex[:12]}",
    )
    title: Mapped[str] = mapped_column(
        String(255),
        default="New conversation",
        nullable=False,
    )
    active_model_id: Mapped[str] = mapped_column(
        String(64),
        default="openai-cloud",
        nullable=False,
    )
    user_metadata_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        ForeignKey("user_metadata.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    user: Mapped[Optional["UserMetadataModel"]] = relationship(
        "UserMetadataModel",
        back_populates="sessions",
    )
    messages: Mapped[List["MessageModel"]] = relationship(
        "MessageModel",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="MessageModel.created_at",
        lazy="selectin",
    )
    artifacts: Mapped[List["ArtifactModel"]] = relationship(
        "ArtifactModel",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ArtifactModel.created_at",
        lazy="selectin",
    )
