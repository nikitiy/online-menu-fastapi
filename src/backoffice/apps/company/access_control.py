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
    """Access control system for checking permissions based on user roles in companies"""

    def __init__(self, session: AsyncSession):
        self.company_member_service = CompanyMemberService(session)

    async def check_menu_item_permission(
        self,
        menu_item: MenuItem,
        user_id: int,
        permission: MenuItemPermission,
    ) -> None:
        """
        Check if user has the required permission for the menu item

        Args:
            menu_item: Menu item to check access for
            user_id: ID of the user
            permission: Required permission

        Raises:
            ForbiddenError: If user doesn't have the required permission
        """
        if menu_item.is_template:
            # Templates don't require company membership check
            return

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
        """
        Check if user has the required permission in the company

        Args:
            company_id: ID of the company
            user_id: ID of the user
            permission: Required permission

        Raises:
            ForbiddenError: If user doesn't have the required permission
        """
        role = await self.company_member_service.get_user_role_in_company(
            user_id, company_id
        )
        if not role:
            raise ForbiddenError("User is not a member of the specified company")

        # Check permission based on role
        if not self._has_permission(role, permission):
            raise ForbiddenError(
                f"User does not have permission to perform this action. "
                f"Required permission: {permission.name}, User role: {role.value}"
            )

    async def check_read_access(self, menu_item: MenuItem, user_id: int) -> None:
        """Check if user can read the menu item"""
        await self.check_menu_item_permission(
            menu_item, user_id, MenuItemPermission.READ
        )

    async def check_create_access(self, company_id: int, user_id: int) -> None:
        """Check if user can create menu items in the company"""
        await self.check_company_permission(
            company_id, user_id, MenuItemPermission.CREATE
        )

    async def check_update_access(self, menu_item: MenuItem, user_id: int) -> None:
        """Check if user can update the menu item"""
        await self.check_menu_item_permission(
            menu_item, user_id, MenuItemPermission.UPDATE
        )

    async def check_delete_access(self, menu_item: MenuItem, user_id: int) -> None:
        """Check if user can delete the menu item"""
        await self.check_menu_item_permission(
            menu_item, user_id, MenuItemPermission.DELETE
        )

    async def can_user_read_in_company(self, user_id: int, company_id: int) -> bool:
        """
        Check if user can read menu items in the company
        Returns True if user has read permission, False otherwise
        """
        role = await self.company_member_service.get_user_role_in_company(
            user_id, company_id
        )
        return role is not None and can_read(role)

    def _has_permission(
        self, role: CompanyRole, permission: MenuItemPermission
    ) -> bool:
        """Internal method to check if role has the required permission"""
        permission_checkers = {
            MenuItemPermission.READ: can_read,
            MenuItemPermission.CREATE: can_create,
            MenuItemPermission.UPDATE: can_update,
            MenuItemPermission.DELETE: can_delete,
        }

        checker = permission_checkers.get(permission)
        return checker is not None and checker(role)
