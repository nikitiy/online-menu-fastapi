from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.company.models import CompanyMember
from src.backoffice.apps.company.models.types import CompanyRole
from src.backoffice.apps.company.repositories import (CompanyMemberRepository,
                                                      CompanyRepository)
from src.backoffice.apps.company.schemas import CompanyMemberCreate


class CompanyMemberService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = CompanyMemberRepository(session)
        self.company_repository = CompanyRepository(session)

    async def add_member(
        self, company_id: int, member_data: CompanyMemberCreate
    ) -> CompanyMember:
        company = await self.company_repository.get_by_id(company_id)
        if not company:
            raise ValueError("Company not found")

        existing_member = await self.repository.get_by_company_and_user(
            company_id, member_data.user_id
        )
        if existing_member:
            raise ValueError("User is already a member of this company")

        if member_data.role == CompanyRole.OWNER:
            existing_owner = await self.repository.get_owner(company_id)
            if existing_owner:
                raise ValueError("Company already has an owner")

        member = await self.repository.create(
            company_id=company_id,
            user_id=member_data.user_id,
            role=member_data.role,
        )

        return member
