from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.company.models.types import CompanyRole
from src.backoffice.apps.company.permissions import (
    MenuItemPermission,
    can_create,
    can_delete,
    can_read,
    can_update,
)
from src.backoffice.apps.company.services import CompanyMemberService
from src.backoffice.apps.menu.models import MenuItem
from src.backoffice.core.exceptions import ForbiddenError


class CompanyAccessControl:
    def __init__(self, session: AsyncSession):
        self.company_member_service = CompanyMemberService(session)

    async def check_menu_item_permission(
        self,
        menu_item: MenuItem,
        user_id: int,
        permission: MenuItemPermission,
    ) -> None:
        if not menu_item.owner_company_id:
            raise ForbiddenError(
                "Menu item must belong to a company for access control"
            )

        await self.check_company_permission(
            company_id=menu_item.owner_company_id,
            user_id=user_id,
            permission=permission,
        )

    async def check_company_permission(
        self,
        company_id: int,
        user_id: int,
        permission: MenuItemPermission,
    ) -> None:
        role = await self.company_member_service.get_user_role_in_company(
            user_id, company_id
        )
        if not role:
            raise ForbiddenError("User is not a member of the specified company")

        if not self._has_permission(role, permission):
            raise ForbiddenError(
                f"User does not have permission to {permission.name.lower()} menu items. "
                f"Required permission: {permission.name}, User role: {role.value}"
            )

    async def check_menu_item_read_access(
        self, menu_item: MenuItem, user_id: int
    ) -> None:
        await self.check_menu_item_permission(
            menu_item, user_id, MenuItemPermission.READ
        )

    async def check_menu_item_create_access(
        self, company_id: int, user_id: int
    ) -> None:
        await self.check_company_permission(
            company_id, user_id, MenuItemPermission.CREATE
        )

    async def check_menu_item_update_access(
        self, menu_item: MenuItem, user_id: int
    ) -> None:
        await self.check_menu_item_permission(
            menu_item, user_id, MenuItemPermission.UPDATE
        )

    async def check_menu_item_delete_access(
        self, menu_item: MenuItem, user_id: int
    ) -> None:
        await self.check_menu_item_permission(
            menu_item, user_id, MenuItemPermission.DELETE
        )

    async def can_user_read_in_company(self, user_id: int, company_id: int) -> bool:
        role = await self.company_member_service.get_user_role_in_company(
            user_id, company_id
        )
        return role is not None and can_read(role)

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

    def _has_permission(
        self, role: CompanyRole, permission: MenuItemPermission
    ) -> bool:
        permission_checkers = {
            MenuItemPermission.READ: can_read,
            MenuItemPermission.CREATE: can_create,
            MenuItemPermission.UPDATE: can_update,
            MenuItemPermission.DELETE: can_delete,
        }

        checker = permission_checkers.get(permission)
        return checker is not None and checker(role)
