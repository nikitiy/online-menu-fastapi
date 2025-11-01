from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.location.models import Street
from src.backoffice.core.repositories import BaseRepository


class StreetRepository(BaseRepository[Street]):
    def __init__(self, session: AsyncSession):
        super().__init__(Street, session)

    async def get_by_city_id(
        self, city_id: int, skip: int = 0, limit: int = 100
    ) -> List[Street]:
        result = await self.session.execute(
            select(Street).where(Street.city_id == city_id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_name(self, name: str, city_id: int) -> Optional[Street]:
        result = await self.session.execute(
            select(Street).where(
                Street.name.ilike(f"%{name}%"),
                Street.city_id == city_id,
            )
        )
        return result.scalar_one_or_none()
