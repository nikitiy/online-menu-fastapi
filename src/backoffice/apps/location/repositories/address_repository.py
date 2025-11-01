from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.location.models import Address
from src.backoffice.core.repositories import BaseRepository


class AddressRepository(BaseRepository[Address]):
    def __init__(self, session: AsyncSession):
        super().__init__(Address, session)

    async def get_by_street_id(
        self, street_id: int, skip: int = 0, limit: int = 100
    ) -> List[Address]:
        result = await self.session.execute(
            select(Address)
            .where(Address.street_id == street_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
