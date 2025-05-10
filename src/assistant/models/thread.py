from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, JSON, String
from sqlalchemy.dialects.postgresql import UUID

from assistant.models.base import Base


class Thread(Base):
    """Thread model for storing conversation threads."""
    
    __tablename__ = "threads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_data = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow) 