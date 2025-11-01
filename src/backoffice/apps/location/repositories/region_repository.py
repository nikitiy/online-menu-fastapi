from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.location.models import Region
from src.backoffice.core.repositories import BaseRepository


class RegionRepository(BaseRepository[Region]):
    def __init__(self, session: AsyncSession):
        super().__init__(Region, session)

    async def get_by_country_id(
        self, country_id: int, skip: int = 0, limit: int = 100
    ) -> List[Region]:
        result = await self.session.execute(
            select(Region)
            .where(Region.country_id == country_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_name(self, name: str, country_id: int) -> Optional[Region]:
        result = await self.session.execute(
            select(Region).where(
                Region.name.ilike(f"%{name}%"),
                Region.country_id == country_id,
            )
        )
        return result.scalar_one_or_none()
