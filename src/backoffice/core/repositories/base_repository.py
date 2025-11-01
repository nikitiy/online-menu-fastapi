from abc import ABC
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy import Select, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.backoffice.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(ABC, Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, **kwargs: Any) -> ModelType:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)  # type: ignore
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_relations(
        self, id: int, relations: List[str]
    ) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)  # type: ignore

        for relation in relations:
            query = query.options(selectinload(getattr(self.model, relation)))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
    ) -> List[ModelType]:
        query = select(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)  # type: ignore

        if order_by and hasattr(self.model, order_by):
            query = query.order_by(getattr(self.model, order_by))

        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, id: int, **kwargs: Any) -> Optional[ModelType]:
        update_data = {k: v for k, v in kwargs.items() if v is not None}

        if not update_data:
            return await self.get_by_id(id)

        await self.session.execute(
            update(self.model)
            .where(self.model.id == id)  # type: ignore
            .values(**update_data)
        )
        await self.session.flush()

        return await self.get_by_id(id)

    async def delete(self, id: int) -> bool:
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)  # type: ignore
        )
        return result.rowcount > 0  # type: ignore

    async def exists(self, id: int) -> bool:
        result = await self.session.execute(
            select(self.model.id).where(self.model.id == id)  # type: ignore
        )
        return result.scalar_one_or_none() is not None

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        query = select(self.model.id)  # type: ignore

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)  # type: ignore

        result = await self.session.execute(query)
        return len(result.scalars().all())

    def _build_query(self) -> Select:
        return select(self.model)

    async def execute_query(self, query: Select) -> List[ModelType]:
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def execute_scalar_query(self, query: Select) -> Any:
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
