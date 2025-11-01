from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.location.models import Region
from src.backoffice.apps.location.repositories import RegionRepository
from src.backoffice.apps.location.schemas import RegionCreate


class RegionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = RegionRepository(session)

    async def create_region(self, region_data: RegionCreate):
        return await self.repository.create(**region_data.model_dump(exclude_none=True))

    async def get_region(self, region_id: int):
        return await self.repository.get_by_id(region_id)

    async def get_regions_by_country(self, country_id: int) -> List[Region]:
        return await self.repository.get_by_country_id(country_id)

    async def update_region(self, region_id: int, region_data: dict):
        return await self.repository.update(region_id, **region_data)

    async def delete_region(self, region_id: int) -> bool:
        return await self.repository.delete(region_id)
