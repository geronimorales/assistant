from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ThreadBase(BaseModel):
    """Base schema for Thread."""
    user_data: Dict = Field(default_factory=dict)


class ThreadCreate(ThreadBase):
    """Schema for creating a new Thread."""
    pass


class ThreadUpdate(ThreadBase):
    """Schema for updating a Thread."""
    user_data: Optional[Dict] = None


class ThreadInDB(ThreadBase):
    """Schema for Thread as stored in database."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class Thread(ThreadInDB):
    """Schema for Thread as returned to client."""
    pass 