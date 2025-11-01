from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.company.models import Company, CompanyMember
from src.backoffice.core.repositories import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    def __init__(self, session: AsyncSession):
        super().__init__(Company, session)

    async def subdomain_exists(self, subdomain: str) -> bool:
        stmt = select(Company.id).where(Company.subdomain == subdomain)

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def select_user_companies(
        self,
        user_id: int,
    ) -> List[Company]:
        stmt = (
            select(Company)
            .join(CompanyMember, Company.id == CompanyMember.company_id)
            .where(CompanyMember.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
