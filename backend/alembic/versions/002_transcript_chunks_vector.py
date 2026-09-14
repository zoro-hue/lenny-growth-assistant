"""Add transcript_chunks table with pgvector embeddings

Revision ID: 002_transcript_chunks_vector
Revises: 001_initial_schema
Create Date: 2026-09-13 18:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '002_transcript_chunks_vector'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == 'postgresql'

    if is_postgres:
        op.execute('CREATE EXTENSION IF NOT EXISTS vector;')

    op.create_table(
        'transcript_chunks',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('transcript_id', sa.String(length=64), nullable=False),
        sa.Column('episode_number', sa.Integer(), nullable=True),
        sa.Column('episode_title', sa.String(length=255), nullable=False),
        sa.Column('guest', sa.String(length=128), nullable=False),
        sa.Column('guest_role', sa.String(length=255), nullable=True),
        sa.Column('source_url', sa.String(length=512), nullable=True),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.String(length=32), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('token_count', sa.Integer(), nullable=True),
        sa.Column('embedding', Vector(1536), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['transcript_id'], ['transcript_metadata.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transcript_chunks_transcript_id'), 'transcript_chunks', ['transcript_id'], unique=False)
    op.create_index(op.f('ix_transcript_chunks_guest'), 'transcript_chunks', ['guest'], unique=False)
    op.create_index(op.f('ix_transcript_chunks_chunk_index'), 'transcript_chunks', ['chunk_index'], unique=False)
    op.create_index(op.f('ix_transcript_chunks_episode_number'), 'transcript_chunks', ['episode_number'], unique=False)

    if is_postgres:
        op.execute(
            'CREATE INDEX IF NOT EXISTS ix_transcript_chunks_embedding ON transcript_chunks '
            'USING hnsw (embedding vector_cosine_ops);'
        )


def downgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == 'postgresql'
    if is_postgres:
        op.execute('DROP INDEX IF EXISTS ix_transcript_chunks_embedding;')
    op.drop_table('transcript_chunks')
