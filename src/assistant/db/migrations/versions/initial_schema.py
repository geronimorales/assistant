"""Initial schema

Revision ID: initial_schema
Revises: 
Create Date: 2024-03-21

"""
import os
from dotenv import load_dotenv

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector

load_dotenv()

# revision identifiers, used by Alembic.
revision: str = 'initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable vector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create threads table
    op.create_table(
        'threads',
        sa.Column('id', UUID, primary_key=True),
        sa.Column('user_data', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    dimension = int(os.getenv('LLM_OLLAMA_EMBEDDING_DIMENSION', 768))
    # Create data_embeddings table
    op.create_table(
        'data_embeddings',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('text', sa.Text, nullable=False),
        sa.Column('metadata_', sa.JSON, nullable=True),
        sa.Column('node_id', sa.String, nullable=True),
        sa.Column('embedding', Vector(dimension), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('data_embeddings')
    op.drop_table('threads')
    
    # Disable vector extension
    op.execute('DROP EXTENSION IF EXISTS vector')