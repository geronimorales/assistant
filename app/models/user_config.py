from uuid import uuid4

from sqlalchemy import Column, Boolean, JSON, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func

from app.models.base import Base

class UserConfig(Base):
    """SQLAlchemy model for user configurations."""
    __tablename__ = "user_configs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    description = Column(String, nullable=True)
    config = Column(JSON, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)