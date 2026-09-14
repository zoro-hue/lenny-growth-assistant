import uuid
from sqlalchemy import String, Text, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin


class ArtifactModel(Base, TimestampMixin):
    __tablename__ = "artifacts"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: f"artifact-{uuid.uuid4().hex[:12]}",
    )
    session_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    type: Mapped[str] = mapped_column(
        String(32),
        default="markdown",  # 'markdown' | 'html'
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )
    word_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    source_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    allow_scripts: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Relationship back to session
    session: Mapped["SessionModel"] = relationship(
        "SessionModel",
        back_populates="artifacts",
    )
