from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.backoffice.apps.company.models import CompanyMember
from src.backoffice.apps.company.models.types import CompanyRole
from src.backoffice.core.repositories import BaseRepository


class CompanyMemberRepository(BaseRepository[CompanyMember]):
    def __init__(self, session: AsyncSession):
        super().__init__(CompanyMember, session)

    async def get_by_company_and_user(
        self, company_id: int, user_id: int
    ) -> Optional[CompanyMember]:
        result = await self.session.execute(
            select(CompanyMember).where(
                CompanyMember.company_id == company_id, CompanyMember.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def get_owner(self, company_id: int) -> Optional[CompanyMember]:
        result = await self.session.execute(
            select(CompanyMember)
            .where(
                CompanyMember.company_id == company_id,
                CompanyMember.role == CompanyRole.OWNER,
            )
            .options(selectinload(CompanyMember.user))
        )
        return result.scalar_one_or_none()
