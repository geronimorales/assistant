from typing import Dict, Optional
from uuid import UUID

from assistant.models.thread import Thread
from assistant.repositories.base import BaseRepository
from assistant.schemas.thread import ThreadCreate, ThreadUpdate


class ThreadRepository(BaseRepository[Thread, ThreadCreate, ThreadUpdate]):
    """Repository for Thread operations."""

    def __init__(self):
        super().__init__(Thread)

    async def create_with_user_data(
        self, *, user_data: Optional[Dict] = None
    ) -> Thread:
        """Create a new thread with optional user data."""
        thread_data = ThreadCreate(user_data=user_data or {})
        return await self.create(obj_in=thread_data)

    async def get_by_id(self, thread_id: UUID) -> Optional[Thread]:
        """Get a thread by its ID."""
        return await self.get(id=thread_id)

    async def update_user_data(
        self, *, thread_id: UUID, user_data: Dict
    ) -> Optional[Thread]:
        """Update a thread's user data."""
        thread = await self.get_by_id(thread_id=thread_id)
        if not thread:
            return None
        
        update_data = ThreadUpdate(user_data=user_data)
        return await self.update(db_obj=thread, obj_in=update_data) 