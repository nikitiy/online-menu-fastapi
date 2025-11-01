from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.location.models import Street
from src.backoffice.apps.location.repositories import StreetRepository
from src.backoffice.apps.location.schemas import StreetCreate


class StreetService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = StreetRepository(session)

    async def create_street(self, street_data: StreetCreate):
        return await self.repository.create(**street_data.model_dump(exclude_none=True))

    async def get_street(self, street_id: int):
        return await self.repository.get_by_id(street_id)

    async def get_streets_by_city(self, city_id: int) -> List[Street]:
        return await self.repository.get_by_city_id(city_id)

    async def update_street(self, street_id: int, street_data: dict):
        return await self.repository.update(street_id, **street_data)

    async def delete_street(self, street_id: int) -> bool:
        return await self.repository.delete(street_id)
