from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.location.models import City
from src.backoffice.apps.location.repositories import CityRepository
from src.backoffice.apps.location.schemas import CityCreate


class CityService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = CityRepository(session)

    async def create_city(self, city_data: CityCreate):
        return await self.repository.create(**city_data.model_dump(exclude_none=True))

    async def get_city(self, city_id: int):
        return await self.repository.get_by_id(city_id)

    async def get_cities_by_country(self, country_id: int) -> List[City]:
        return await self.repository.get_by_country_id(country_id)

    async def get_cities_by_region(self, region_id: int) -> List[City]:
        return await self.repository.get_by_region_id(region_id)

    async def update_city(self, city_id: int, city_data: dict):
        return await self.repository.update(city_id, **city_data)

    async def delete_city(self, city_id: int) -> bool:
        return await self.repository.delete(city_id)
