from enum import IntEnum

from src.backoffice.apps.company.models.types import CompanyRole


class MenuItemPermission(IntEnum):
    READ = 1  # View menu items
    CREATE = 2  # Create menu items
    UPDATE = 3  # Update menu items
    DELETE = 4  # Delete menu items


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
    },
    CompanyRole.EDITOR: {
        MenuItemPermission.READ,
        MenuItemPermission.CREATE,
        MenuItemPermission.UPDATE,
        MenuItemPermission.DELETE,
    },
    CompanyRole.ADMIN: {
        MenuItemPermission.READ,
        MenuItemPermission.CREATE,
        MenuItemPermission.UPDATE,
        MenuItemPermission.DELETE,
    },
    CompanyRole.OWNER: {
        MenuItemPermission.READ,
        MenuItemPermission.CREATE,
        MenuItemPermission.UPDATE,
        MenuItemPermission.DELETE,
    },
}


def has_permission(role: CompanyRole, permission: MenuItemPermission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())


def can_read(role: CompanyRole) -> bool:
    return has_permission(role, MenuItemPermission.READ)


def can_create(role: CompanyRole) -> bool:
    return has_permission(role, MenuItemPermission.CREATE)


def can_update(role: CompanyRole) -> bool:
    return has_permission(role, MenuItemPermission.UPDATE)


def can_delete(role: CompanyRole) -> bool:
    return has_permission(role, MenuItemPermission.DELETE)
