from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.location.models import City
from src.backoffice.core.repositories import BaseRepository


class CityRepository(BaseRepository[City]):
    def __init__(self, session: AsyncSession):
        super().__init__(City, session)

    async def get_by_country_id(
        self, country_id: int, skip: int = 0, limit: int = 100
    ) -> List[City]:
        result = await self.session.execute(
            select(City).where(City.country_id == country_id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_region_id(
        self, region_id: int, skip: int = 0, limit: int = 100
    ) -> List[City]:
        result = await self.session.execute(
            select(City).where(City.region_id == region_id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_country_and_region_id(
        self,
        country_id: int,
        region_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[City]:
        stmt = select(City).where(City.country_id == country_id)
        if region_id is not None:
            stmt = stmt.where(City.region_id == region_id)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_name(
        self,
        name: str,
        country_id: int,
        region_id: Optional[int] = None,
    ) -> Optional[City]:
        conditions = [
            City.name.ilike(f"%{name}%"),
            City.country_id == country_id,
        ]
        if region_id is not None:
            conditions.append(City.region_id == region_id)

        stmt = select(City).where(*conditions)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
