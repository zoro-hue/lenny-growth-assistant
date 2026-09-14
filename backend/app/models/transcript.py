import uuid
from typing import Optional, List
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from .base import Base, TimestampMixin


class TranscriptMetadataModel(Base, TimestampMixin):
    """
    Document metadata entity storing Lenny's Podcast episode archives,
    prepared for pgvector chunk embeddings in Phase 3.
    """
    __tablename__ = "transcript_metadata"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: f"ep-{uuid.uuid4().hex[:12]}",
    )
    episode_number: Mapped[Optional[int]] = mapped_column(
        Integer,
        index=True,
        nullable=True,
    )
    episode_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    guest: Mapped[str] = mapped_column(
        String(128),
        index=True,
        nullable=False,
    )
    guest_role: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    published_date: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    audio_url: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )
    transcript_url: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )
    duration_seconds: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    chunk_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Relationships
    chunks: Mapped[List["TranscriptChunkModel"]] = relationship(
        "TranscriptChunkModel",
        back_populates="transcript",
        cascade="all, delete-orphan",
    )


class TranscriptChunkModel(Base, TimestampMixin):
    """
    Passage chunk entity storing split transcript text and pgvector embeddings
    for semantic similarity retrieval.
    """
    __tablename__ = "transcript_chunks"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: f"chk-{uuid.uuid4().hex[:12]}",
    )
    transcript_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("transcript_metadata.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    episode_number: Mapped[Optional[int]] = mapped_column(
        Integer,
        index=True,
        nullable=True,
    )
    episode_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    guest: Mapped[str] = mapped_column(
        String(128),
        index=True,
        nullable=False,
    )
    guest_role: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    source_url: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )
    chunk_index: Mapped[int] = mapped_column(
        Integer,
        index=True,
        nullable=False,
    )
    timestamp: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    token_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    embedding = mapped_column(
        Vector(1536),
        nullable=True,
    )

    # Relationship back to episode metadata
    transcript: Mapped["TranscriptMetadataModel"] = relationship(
        "TranscriptMetadataModel",
        back_populates="chunks",
    )
