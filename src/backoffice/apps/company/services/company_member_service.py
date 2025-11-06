from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.account.services import UserService
from src.backoffice.apps.company.models import CompanyMember
from src.backoffice.apps.company.models.types import CompanyRole
from src.backoffice.apps.company.repositories import (
    CompanyMemberRepository,
    CompanyRepository,
)
from src.backoffice.apps.company.schemas import (
    CompanyMemberCreate,
    CompanyMemberCreateByEmail,
    CompanyMemberUpdateByEmail,
)
from src.backoffice.core.exceptions import NotFoundError


class CompanyMemberService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = CompanyMemberRepository(session)
        self.company_repository = CompanyRepository(session)
        self.user_service = UserService(session)

    async def add_member(
        self, company_id: int, member_data: CompanyMemberCreate
    ) -> CompanyMember:
        company = await self.company_repository.get_by_id(company_id)
        if not company:
            raise NotFoundError(f"Company with id {company_id} not found")

        await self._ensure_member_not_exists(company_id, member_data.user_id)

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

    async def get_user_role_in_company(
        self, user_id: int, company_id: int
    ) -> CompanyRole | None:
        member = await self.repository.get_by_company_and_user(company_id, user_id)
        return member.role if member else None

    async def _ensure_member_not_exists(self, company_id: int, user_id: int) -> None:
        existing_member = await self.repository.get_by_company_and_user(
            company_id, user_id
        )
        if existing_member:
            raise ValueError("User is already a member of this company")

    async def _get_member_or_raise(
        self, company_id: int, user_id: int
    ) -> CompanyMember:
        member = await self.repository.get_by_company_and_user(company_id, user_id)
        if not member:
            raise NotFoundError("User is not a member of this company")
        return member

    async def add_member_by_email(
        self, company_id: int, member_data: CompanyMemberCreateByEmail
    ) -> CompanyMember:
        company = await self.company_repository.get_by_id(company_id)
        if not company:
            raise NotFoundError(f"Company with id {company_id} not found")

        user = await self.user_service.get_by_email(member_data.user_email)
        if not user:
            raise NotFoundError(f"User with email {member_data.user_email} not found")

        await self._ensure_member_not_exists(company_id, user.id)

        member = await self.repository.create(
            company_id=company_id,
            user_id=user.id,
            role=CompanyRole.VIEWER,
        )

        return member

    async def remove_member_by_email(self, company_id: int, user_email: str) -> None:
        company = await self.company_repository.get_by_id(company_id)
        if not company:
            raise NotFoundError(f"Company with id {company_id} not found")

        user = await self.user_service.get_by_email(user_email)
        if not user:
            raise NotFoundError(f"User with email {user_email} not found")

        member = await self._get_member_or_raise(company_id, user.id)

        if member.role == CompanyRole.OWNER:
            raise ValueError("Cannot remove owner from the company")

        await self.repository.delete(member.id)

    async def update_member_role_by_email(
        self, company_id: int, member_data: CompanyMemberUpdateByEmail
    ) -> CompanyMember:
        company = await self.company_repository.get_by_id(company_id)
        if not company:
            raise NotFoundError(f"Company with id {company_id} not found")

        user = await self.user_service.get_by_email(member_data.user_email)
        if not user:
            raise NotFoundError(f"User with email {member_data.user_email} not found")

        member = await self._get_member_or_raise(company_id, user.id)

        if member.role == CompanyRole.OWNER:
            raise ValueError("Cannot change owner role")

        updated_member = await self.repository.update(member.id, role=member_data.role)
        if not updated_member:
            raise ValueError("Failed to update member role")

        return updated_member
