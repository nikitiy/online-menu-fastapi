from enum import IntEnum
from typing import Protocol, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.company.models.types import CompanyRole
from src.backoffice.apps.company.services import CompanyMemberService
from src.backoffice.core.exceptions import ForbiddenError

PermissionType = TypeVar("PermissionType", bound=IntEnum)


class PermissionChecker(Protocol[PermissionType]):
    def __call__(self, role: CompanyRole, permission: PermissionType) -> bool: ...


class CompanyAccessControl:

    def __init__(self, session: AsyncSession):
        self.company_member_service = CompanyMemberService(session)

    async def check_company_permission(
        self,
        company_id: int,
        user_id: int,
        permission: PermissionType,
        permission_checker: PermissionChecker[PermissionType],
    ) -> None:
        role = await self.company_member_service.get_user_role_in_company(
            user_id, company_id
        )
        if not role:
            raise ForbiddenError("User is not a member of the specified company")

        if not permission_checker(role, permission):
            raise ForbiddenError(
                f"User does not have permission to {permission.name.lower()}. "
                f"Required permission: {permission.name}, User role: {role.value}"
            )

    async def check_resource_permission(
        self,
        resource_company_id: int,
        user_id: int,
        permission: PermissionType,
        permission_checker: PermissionChecker[PermissionType],
    ) -> None:
        if not resource_company_id:
            raise ForbiddenError("Resource must belong to a company for access control")

        await self.check_company_permission(
            company_id=resource_company_id,
            user_id=user_id,
            permission=permission,
            permission_checker=permission_checker,
        )

    async def check_can_add_member(self, company_id: int, user_id: int) -> None:
        requester_role = await self.company_member_service.get_user_role_in_company(
            user_id, company_id
        )
        if not requester_role:
            raise ForbiddenError("User is not a member of the specified company")

        if requester_role not in (CompanyRole.ADMIN, CompanyRole.OWNER):
            raise ForbiddenError(
                f"User does not have permission to add members. "
                f"Required role: ADMIN or OWNER, User role: {requester_role.value}"
            )

    async def _check_admin_can_modify_user(
        self, company_id: int, target_user_id: int, action: str
    ) -> None:
        target_user_current_role = (
            await self.company_member_service.get_user_role_in_company(
                target_user_id, company_id
            )
        )
        if target_user_current_role in (CompanyRole.ADMIN, CompanyRole.OWNER):
            raise ForbiddenError(
                f"ADMIN cannot {action} user with {target_user_current_role.value} role. "
                f"Only OWNER can {action} ADMIN and OWNER."
            )

    async def _check_requester_role(
        self, company_id: int, user_id: int, required_roles: tuple[CompanyRole, ...]
    ) -> CompanyRole:
        requester_role = await self.company_member_service.get_user_role_in_company(
            user_id, company_id
        )
        if not requester_role:
            raise ForbiddenError("User is not a member of the specified company")

        if requester_role not in required_roles:
            roles_str = " or ".join(role.value.upper() for role in required_roles)
            raise ForbiddenError(
                f"User does not have required permission. "
                f"Required role: {roles_str}, User role: {requester_role.value}"
            )

        return requester_role

    async def check_can_remove_member(
        self, company_id: int, user_id: int, target_user_id: int
    ) -> None:
        requester_role = await self._check_requester_role(
            company_id, user_id, (CompanyRole.ADMIN, CompanyRole.OWNER)
        )

        if requester_role == CompanyRole.OWNER:
            return

        if requester_role == CompanyRole.ADMIN:
            await self._check_admin_can_modify_user(
                company_id, target_user_id, "remove"
            )
            return

    async def check_can_change_role(
        self,
        company_id: int,
        user_id: int,
        target_user_id: int,
        target_role: CompanyRole,
    ) -> None:
        requester_role = await self._check_requester_role(
            company_id, user_id, (CompanyRole.ADMIN, CompanyRole.OWNER)
        )

        if requester_role == CompanyRole.OWNER:
            return

        if requester_role == CompanyRole.ADMIN:
            await self._check_admin_can_modify_user(
                company_id, target_user_id, "change role of"
            )

            if target_role == CompanyRole.ADMIN:
                raise ForbiddenError(
                    "ADMIN cannot change role to ADMIN. Only OWNER can assign ADMIN role."
                )
            if target_role == CompanyRole.OWNER:
                raise ForbiddenError(
                    "ADMIN cannot change role to OWNER. Only OWNER can assign OWNER role."
                )
            return
