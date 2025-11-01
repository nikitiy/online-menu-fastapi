from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.location.models import Country
from src.backoffice.apps.location.repositories import CountryRepository
from src.backoffice.apps.location.schemas import CountryCreate, CountryUpdate


class CountryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = CountryRepository(session)

    async def create_country(self, country_data: CountryCreate):
        return await self.repository.create(
            **country_data.model_dump(exclude_none=True)
        )

    async def get_country(self, country_id: int):
        return await self.repository.get_by_id(country_id)

    async def get_countries(self) -> List[Country]:
        return await self.repository.get_all_countries()

    async def update_country(self, country_id: int, country_data: CountryUpdate):
        return await self.repository.update(
            country_id, **country_data.model_dump(exclude_unset=True)
        )

    async def delete_country(self, country_id: int) -> bool:
        return await self.repository.delete(country_id)
