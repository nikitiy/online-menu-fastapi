from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.company.models import Company, CompanyBranch
from src.backoffice.apps.company.models.types import CompanyRole
from src.backoffice.apps.company.schemas import (
    CompanyBranchCreate,
    CompanyBranchUpdate,
    CompanyCreate,
    CompanyMemberCreate,
)
from src.backoffice.apps.company.services import (
    CompanyBranchService,
    CompanyMemberService,
    CompanyService,
)


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

    # Company Branch methods
    async def create_branch(self, branch_data: CompanyBranchCreate) -> CompanyBranch:
        branch = await self.company_branch_service.create_branch(branch_data)
        await self.session.commit()
        return branch

    async def get_branch_by_id(self, branch_id: int) -> CompanyBranch:
        return await self.company_branch_service.get_branch_by_id_or_raise(branch_id)

    async def get_branches_by_company(self, company_id: int) -> List[CompanyBranch]:
        return await self.company_branch_service.get_branches_by_company(company_id)

    async def update_branch(
        self, branch_id: int, branch_data: CompanyBranchUpdate
    ) -> CompanyBranch:
        branch = await self.company_branch_service.update_branch_or_raise(
            branch_id, branch_data
        )
        await self.session.commit()
        return branch

    async def delete_branch(self, branch_id: int) -> None:
        await self.company_branch_service.delete_branch_or_raise(branch_id)
        await self.session.commit()
