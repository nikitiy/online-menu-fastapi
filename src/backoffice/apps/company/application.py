from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.account.services import UserService
from src.backoffice.apps.company.access_control import CompanyAccessControl
from src.backoffice.apps.company.models import Company, CompanyBranch
from src.backoffice.apps.company.models.types import CompanyRole
from src.backoffice.apps.company.schemas import (
    CompanyBranchCreate,
    CompanyBranchUpdate,
    CompanyCreate,
    CompanyMemberCreate,
    CompanyMemberCreateByEmail,
    CompanyMemberCreateByEmailResponse,
    CompanyMemberResponse,
    CompanyMemberUpdateByEmail,
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
        self.user_service = UserService(session)
        self.access_control = CompanyAccessControl(session)

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

    # Company Member methods
    async def add_member_by_email(
        self,
        company_subdomain: str,
        member_data: CompanyMemberCreateByEmail,
        user_id: int,
    ) -> CompanyMemberCreateByEmailResponse:
        company = await self.company_service.get_by_subdomain_or_raise(
            company_subdomain
        )
        await self.access_control.check_can_add_member(company.id, user_id)
        member = await self.company_member_service.add_member_by_email(
            company.id, member_data
        )
        await self.session.commit()
        return CompanyMemberCreateByEmailResponse(
            message=f"User {member_data.user_email} has been added to the company with role VIEWER",
            company_member=CompanyMemberResponse.model_validate(member),
        )

    async def remove_member_by_email(
        self,
        company_subdomain: str,
        user_email: str,
        user_id: int,
    ) -> None:
        company = await self.company_service.get_by_subdomain_or_raise(
            company_subdomain
        )
        target_member = await self.company_member_service.get_member_by_email_or_raise(
            company.id, user_email
        )
        await self.access_control.check_can_remove_member(
            company.id, user_id, target_member.user_id
        )
        await self.company_member_service.remove_member_by_email(company.id, user_email)
        await self.session.commit()

    async def update_member_role_by_email(
        self,
        company_subdomain: str,
        member_data: CompanyMemberUpdateByEmail,
        user_id: int,
    ) -> CompanyMemberResponse:
        company = await self.company_service.get_by_subdomain_or_raise(
            company_subdomain
        )
        target_member = await self.company_member_service.get_member_by_email_or_raise(
            company.id, member_data.user_email
        )
        await self.access_control.check_can_change_role(
            company.id, user_id, target_member.user_id, member_data.role
        )
        member = await self.company_member_service.update_member_role_by_email(
            company.id, member_data
        )
        await self.session.commit()
        return CompanyMemberResponse.model_validate(member)
