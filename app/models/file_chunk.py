from typing import Dict, Optional

from sqlalchemy import Column, String, JSON, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector

from app.models.base import Base

class FileChunk(Base):
    """Model for storing file chunks with embeddings."""
    
    __tablename__ = "data_embeddings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text, nullable=False)
    metadata_ = Column(JSON, nullable=True)
    node_id = Column(String, nullable=True)
    embedding = Column(Vector(768), nullable=True)  # Using 1536 dimensions for OpenAI embeddings 