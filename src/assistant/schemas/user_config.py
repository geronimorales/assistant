from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

class UserConfigBase(BaseModel):
    """Base Pydantic model for user configurations."""
    description: Optional[str] = None
    config: Dict[str, Any]
    active: bool = True

class UserConfigCreate(UserConfigBase):
    """Pydantic model for creating a user configuration."""
    pass

class UserConfigUpdate(UserConfigBase):
    """Pydantic model for updating a user configuration."""
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    active: Optional[bool] = None

class UserConfigInDB(UserConfigBase):
    """Pydantic model for user configuration as stored in database."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserConfig(UserConfigInDB):
    """Schema for UserConfig as returned to client."""
    pass 