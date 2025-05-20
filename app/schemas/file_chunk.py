from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FileChunkBase(BaseModel):
    """Base schema for FileChunk."""
    text: str
    metadata_: Optional[Dict] = Field(default=None, alias="metadata")
    node_id: Optional[str] = None
    embedding: Optional[List[float]] = None


class FileChunkCreate(FileChunkBase):
    """Schema for creating a new FileChunk."""
    pass


class FileChunkUpdate(FileChunkBase):
    """Schema for updating a FileChunk."""
    text: Optional[str] = None


class FileChunkInDB(FileChunkBase):
    """Schema for FileChunk as stored in database."""
    id: UUID

    class Config:
        from_attributes = True 