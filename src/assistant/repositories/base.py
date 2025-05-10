from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from assistant.db.base import Base, get_async_database_url

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base repository with default CRUD operations."""

    def __init__(self, model: Type[ModelType]):
        self.model = model
        self._engine = None
        self._async_session = None

    @property
    async def engine(self):
        """Get or create the database engine."""
        if self._engine is None:
            self._engine = create_async_engine(
                get_async_database_url(),
                echo=False,
            )
        return self._engine

    @property
    async def session(self) -> AsyncSession:
        """Get or create a database session."""
        if self._async_session is None:
            engine = await self.engine
            self._async_session = async_sessionmaker(
                bind=engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
            )
        return self._async_session()

    async def get(self, id: UUID) -> Optional[ModelType]:
        """Get a single record by ID."""
        async with await self.session as session:
            result = await session.execute(select(self.model).filter(self.model.id == id))
            return result.scalar_one_or_none()

    async def get_multi(
        self, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records with pagination."""
        async with await self.session as session:
            result = await session.execute(
                select(self.model).offset(skip).limit(limit)
            )
            return result.scalars().all()

    async def create(
        self, *, obj_in: Union[CreateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Create a new record."""
        async with await self.session as session:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data)
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj

    async def update(
        self,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update a record."""
        async with await self.session as session:
            obj_data = jsonable_encoder(db_obj)
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.model_dump(exclude_unset=True)
            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj

    async def delete(self, *, id: UUID) -> Optional[ModelType]:
        """Delete a record."""
        async with await self.session as session:
            obj = await self.get(id=id)
            if obj:
                await session.delete(obj)
                await session.commit()
            return obj 