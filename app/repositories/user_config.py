from typing import Dict, Optional, List, Any
from uuid import UUID

from app.models.user_config import UserConfig
from app.repositories.base import BaseRepository
from app.schemas.user_config import UserConfigCreate, UserConfigUpdate


class UserConfigRepository(BaseRepository[UserConfig, UserConfigCreate, UserConfigUpdate]):
    """Repository for UserConfig operations."""

    def __init__(self):
        super().__init__(UserConfig)

    async def create_with_config(
        self, *, config: Dict[str, Any], description: Optional[str] = None, active: bool = True
    ) -> UserConfig:
        """Create a new user config with the given configuration."""
        user_config_data = UserConfigCreate(
            config=config,
            description=description,
            active=active
        )
        return await self.create(obj_in=user_config_data)

    async def get_by_id(self, config_id: UUID) -> Optional[UserConfig]:
        """Get a user config by its ID."""
        return await self.get(id=config_id)

    async def get_active(self) -> List[UserConfig]:
        """Get all active user configurations."""
        return await self.get_multi(active=True)

    async def update_config(
        self, *, config_id: UUID, config: Dict[str, Any]
    ) -> Optional[UserConfig]:
        """Update a user config's configuration."""
        user_config = await self.get_by_id(config_id=config_id)
        if not user_config:
            return None
        
        update_data = UserConfigUpdate(config=config)
        return await self.update(db_obj=user_config, obj_in=update_data)

    async def update_description(
        self, *, config_id: UUID, description: str
    ) -> Optional[UserConfig]:
        """Update a user config's description."""
        user_config = await self.get_by_id(config_id=config_id)
        if not user_config:
            return None
        
        update_data = UserConfigUpdate(description=description)
        return await self.update(db_obj=user_config, obj_in=update_data)

    async def toggle_active(
        self, *, config_id: UUID, active: bool
    ) -> Optional[UserConfig]:
        """Toggle a user config's active status."""
        user_config = await self.get_by_id(config_id=config_id)
        if not user_config:
            return None
        
        update_data = UserConfigUpdate(active=active)
        return await self.update(db_obj=user_config, obj_in=update_data)


