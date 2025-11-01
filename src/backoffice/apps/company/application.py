from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.company.models import Company
from src.backoffice.apps.company.models.types import CompanyRole
from src.backoffice.apps.company.schemas import (CompanyCreate,
                                                 CompanyMemberCreate)
from src.backoffice.apps.company.services import (CompanyBranchService,
                                                  CompanyMemberService,
                                                  CompanyService)


class CompanyApplication:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.company_service = CompanyService(session)
        self.company_member_service = CompanyMemberService(session)
        self.company_branch_service = CompanyBranchService(session)

    async def create_company_with_owner(
        self, company_data: CompanyCreate, owner_user_id: int
    ) -> Company:
        company = await self.company_service.create_company(company_data)

        await self.company_member_service.add_member(
            company.id,
            CompanyMemberCreate(user_id=owner_user_id, role=CompanyRole.OWNER),
        )

        await self.session.commit()

        return company

    async def get_accessible_companies_for_user(self, user_id: int) -> List[Company]:
        return await self.company_service.get_accessible_companies_for_user(user_id)
