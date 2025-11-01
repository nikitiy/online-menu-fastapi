from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.location.models import Address
from src.backoffice.apps.location.repositories import AddressRepository
from src.backoffice.apps.location.schemas import AddressCreate


class AddressService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = AddressRepository(session)

    async def create_address(self, address_data: AddressCreate):
        return await self.repository.create(
            **address_data.model_dump(exclude_none=True)
        )

    async def get_address(self, address_id: int):
        return await self.repository.get_by_id(address_id)

    async def get_addresses_by_street(self, street_id: int) -> List[Address]:
        return await self.repository.get_by_street_id(street_id)

    async def update_address(self, address_id: int, address_data: dict):
        return await self.repository.update(address_id, **address_data)

    async def delete_address(self, address_id: int) -> bool:
        return await self.repository.delete(address_id)
