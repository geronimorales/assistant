from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from assistant.models.base import Base


class Thread(Base):
    """Thread model for storing conversation threads."""
    
    __tablename__ = "threads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_config_id = Column(UUID(as_uuid=True), ForeignKey('user_configs.id', ondelete='SET NULL'), nullable=True)
    user_data = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
