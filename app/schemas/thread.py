from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ThreadBase(BaseModel):
    """Base schema for Thread."""
    user_config_id: UUID
    user_data: Optional[Dict[str, Any]] = None


class ThreadCreate(ThreadBase):
    """Schema for creating a new Thread."""
    pass


class ThreadUpdate(ThreadBase):
    """Schema for updating a Thread."""
    user_data: Optional[Dict[str, Any]] = None


class ThreadInDB(ThreadBase):
    """Schema for Thread as stored in database."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class Thread(ThreadInDB):
    """Schema for Thread as returned to client."""
    pass 