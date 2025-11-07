from enum import IntEnum

from src.backoffice.apps.company.models.types import CompanyRole


class MenuItemPermission(IntEnum):
    READ = 1
    CREATE = 2
    UPDATE = 3
    DELETE = 4


class CompanyBranchPermission(IntEnum):
    READ = 1
    CREATE = 2
    UPDATE = 3
    DELETE = 4


class QRCodePermission(IntEnum):
    READ = 1
    CREATE = 2
    UPDATE = 3
    DELETE = 4


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
        QRCodePermission.READ,
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
        QRCodePermission.READ,
        QRCodePermission.CREATE,
        QRCodePermission.UPDATE,
        QRCodePermission.DELETE,
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
        QRCodePermission.READ,
        QRCodePermission.CREATE,
        QRCodePermission.UPDATE,
        QRCodePermission.DELETE,
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
        QRCodePermission.READ,
        QRCodePermission.CREATE,
        QRCodePermission.UPDATE,
        QRCodePermission.DELETE,
    },
}


def has_permission(
    role: CompanyRole,
    permission: MenuItemPermission | CompanyBranchPermission | QRCodePermission,
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


def can_read_qr_code(role: CompanyRole) -> bool:
    return has_permission(role, QRCodePermission.READ)


def can_create_qr_code(role: CompanyRole) -> bool:
    return has_permission(role, QRCodePermission.CREATE)


def can_update_qr_code(role: CompanyRole) -> bool:
    return has_permission(role, QRCodePermission.UPDATE)


def can_delete_qr_code(role: CompanyRole) -> bool:
    return has_permission(role, QRCodePermission.DELETE)


# Permission checker functions for use with CompanyAccessControl
def check_menu_item_permission(
    role: CompanyRole, permission: MenuItemPermission
) -> bool:
    return has_permission(role, permission)


def check_branch_permission(
    role: CompanyRole, permission: CompanyBranchPermission
) -> bool:
    return has_permission(role, permission)


def check_qr_code_permission(role: CompanyRole, permission: QRCodePermission) -> bool:
    return has_permission(role, permission)
