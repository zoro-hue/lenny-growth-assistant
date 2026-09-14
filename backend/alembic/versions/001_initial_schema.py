"""Initial schema for Lenny Growth Assistant

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-13 17:40:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. user_metadata table
    op.create_table(
        'user_metadata',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('user_identifier', sa.String(length=128), nullable=False),
        sa.Column('preferences', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_metadata_user_identifier'), 'user_metadata', ['user_identifier'], unique=True)

    # 2. sessions table
    op.create_table(
        'sessions',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('active_model_id', sa.String(length=64), nullable=False),
        sa.Column('user_metadata_id', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_metadata_id'], ['user_metadata.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('session_id', sa.String(length=64), nullable=False),
        sa.Column('role', sa.String(length=32), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('citations', sa.JSON(), nullable=False),
        sa.Column('artifact_id', sa.String(length=64), nullable=True),
        sa.Column('error_details', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_session_id'), 'messages', ['session_id'], unique=False)

    # 4. artifacts table
    op.create_table(
        'artifacts',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('session_id', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=32), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('word_count', sa.Integer(), nullable=False),
        sa.Column('source_count', sa.Integer(), nullable=False),
        sa.Column('allow_scripts', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_artifacts_session_id'), 'artifacts', ['session_id'], unique=False)

    # 5. transcript_metadata table
    op.create_table(
        'transcript_metadata',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('episode_number', sa.Integer(), nullable=True),
        sa.Column('episode_title', sa.String(length=255), nullable=False),
        sa.Column('guest', sa.String(length=128), nullable=False),
        sa.Column('guest_role', sa.String(length=255), nullable=True),
        sa.Column('published_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('audio_url', sa.String(length=512), nullable=True),
        sa.Column('transcript_url', sa.String(length=512), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('chunk_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transcript_metadata_episode_number'), 'transcript_metadata', ['episode_number'], unique=False)
    op.create_index(op.f('ix_transcript_metadata_guest'), 'transcript_metadata', ['guest'], unique=False)


def downgrade() -> None:
    op.drop_table('transcript_metadata')
    op.drop_table('artifacts')
    op.drop_table('messages')
    op.drop_table('sessions')
    op.drop_table('user_metadata')
