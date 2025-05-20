from uuid import UUID
from typing import Optional, Dict, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.thread import Thread
from app.repositories.base import BaseRepository
from app.schemas.thread import ThreadCreate, ThreadUpdate

class ThreadRepository(BaseRepository[Thread, ThreadCreate, ThreadUpdate]):
    """Repository for Thread operations."""

    def __init__(self):
        super().__init__(Thread)

    async def create_with_config(
        self, *, user_config_id: UUID = None,
        user_data: Optional[Dict] = None
    ) -> Thread:
        """Create a new thread with optional user config."""
        thread_data = ThreadCreate(
            user_config_id=user_config_id,
            user_data=user_data or {}
        )
        return await self.create(obj_in=thread_data)

    async def get_by_id(self, thread_id: UUID) -> Optional[Thread]:
        """Get a thread by its ID with its relationships loaded."""
        async with await self.session as session:
            result = await session.execute(
                select(Thread)
                .options(selectinload(Thread.user_config))
                .filter(Thread.id == thread_id)
            )
            return result.scalar_one_or_none()

    async def get_by_config(self, user_config_id: UUID) -> List[Thread]:
        """Get all threads for a specific user config."""
        async with await self.session as session:
            result = await session.execute(
                select(Thread)
                .options(selectinload(Thread.user_config))
                .filter(Thread.user_config_id == user_config_id)
            )
            return result.scalars().all()

    async def update_user_data(
        self, *, thread_id: UUID, user_data: Dict
    ) -> Optional[Thread]:
        """Update a thread's user data."""
        thread = await self.get_by_id(thread_id)
        if not thread:
            return None
        
        update_data = ThreadUpdate(user_data=user_data)
        return await self.update(db_obj=thread, obj_in=update_data)
