from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.location.models import Country
from src.backoffice.core.repositories import BaseRepository


class CountryRepository(BaseRepository[Country]):
    def __init__(self, session: AsyncSession):
        super().__init__(Country, session)

    async def get_by_code(self, code: str) -> Optional[Country]:
        result = await self.session.execute(select(Country).where(Country.code == code))
        return result.scalar_one_or_none()

    async def get_by_code_alpha2(self, code_alpha2: str) -> Optional[Country]:
        result = await self.session.execute(
            select(Country).where(Country.code_alpha2 == code_alpha2)
        )
        return result.scalar_one_or_none()

    async def get_all_countries(self) -> List[Country]:
        result = await self.session.execute(select(Country))
        return list(result.scalars().all())

    async def get_by_name(self, name: str) -> Optional[Country]:
        result = await self.session.execute(
            select(Country).where(Country.name.ilike(f"%{name}%"))
        )
        return result.scalar_one_or_none()
