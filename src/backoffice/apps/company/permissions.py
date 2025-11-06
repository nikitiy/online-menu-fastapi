from enum import IntEnum

from src.backoffice.apps.company.models.types import CompanyRole


class MenuItemPermission(IntEnum):
    READ = 1  # View menu items
    CREATE = 2  # Create menu items
    UPDATE = 3  # Update menu items
    DELETE = 4  # Delete menu items


class CompanyBranchPermission(IntEnum):
    READ = 1  # View company branches
    CREATE = 2  # Create company branches
    UPDATE = 3  # Update company branches
    DELETE = 4  # Delete company branches


# Role hierarchy - higher values mean more permissions
ROLE_WEIGHT = {
    CompanyRole.VIEWER: 1,
    CompanyRole.EDITOR: 2,
    CompanyRole.ADMIN: 3,
    CompanyRole.OWNER: 4,
}

# Permissions for each role
ROLE_PERMISSIONS = {
    CompanyRole.VIEWER: {
        MenuItemPermission.READ,
        CompanyBranchPermission.READ,
    },
    CompanyRole.EDITOR: {
        MenuItemPermission.READ,
        MenuItemPermission.CREATE,
        MenuItemPermission.UPDATE,
        MenuItemPermission.DELETE,
        CompanyBranchPermission.READ,
        CompanyBranchPermission.CREATE,
        CompanyBranchPermission.UPDATE,
        CompanyBranchPermission.DELETE,
    },
    CompanyRole.ADMIN: {
        MenuItemPermission.READ,
        MenuItemPermission.CREATE,
        MenuItemPermission.UPDATE,
        MenuItemPermission.DELETE,
        CompanyBranchPermission.READ,
        CompanyBranchPermission.CREATE,
        CompanyBranchPermission.UPDATE,
        CompanyBranchPermission.DELETE,
    },
    CompanyRole.OWNER: {
        MenuItemPermission.READ,
        MenuItemPermission.CREATE,
        MenuItemPermission.UPDATE,
        MenuItemPermission.DELETE,
        CompanyBranchPermission.READ,
        CompanyBranchPermission.CREATE,
        CompanyBranchPermission.UPDATE,
        CompanyBranchPermission.DELETE,
    },
}


def has_permission(
    role: CompanyRole, permission: MenuItemPermission | CompanyBranchPermission
) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())


def can_read_menu_item(role: CompanyRole) -> bool:
    return has_permission(role, MenuItemPermission.READ)


def can_create_menu_item(role: CompanyRole) -> bool:
    return has_permission(role, MenuItemPermission.CREATE)


def can_update_menu_item(role: CompanyRole) -> bool:
    return has_permission(role, MenuItemPermission.UPDATE)


def can_delete_menu_item(role: CompanyRole) -> bool:
    return has_permission(role, MenuItemPermission.DELETE)


def can_read_branch(role: CompanyRole) -> bool:
    return has_permission(role, CompanyBranchPermission.READ)


def can_create_branch(role: CompanyRole) -> bool:
    return has_permission(role, CompanyBranchPermission.CREATE)


def can_update_branch(role: CompanyRole) -> bool:
    return has_permission(role, CompanyBranchPermission.UPDATE)


def can_delete_branch(role: CompanyRole) -> bool:
    return has_permission(role, CompanyBranchPermission.DELETE)
