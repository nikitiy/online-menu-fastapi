from typing import Annotated, TypeAlias

from fastapi import Depends

from src.backoffice.apps.account.application import AccountApplication
from src.backoffice.apps.company.application import CompanyApplication
from src.backoffice.apps.location.application import LocationApplication
from src.backoffice.apps.menu.application import MenuApplication
from src.backoffice.core.dependencies.database import SessionDep

# ==================== SERVICE DEPENDENCIES ====================


async def get_account_application(session: SessionDep) -> AccountApplication:
    return AccountApplication(session)


async def get_company_application(session: SessionDep) -> CompanyApplication:
    return CompanyApplication(session)


async def get_location_application(session: SessionDep) -> LocationApplication:
    return LocationApplication(session)


async def get_menu_application(session: SessionDep) -> MenuApplication:
    return MenuApplication(session)


# ==================== ANNOTATED TYPES ====================

# Account Application
AccountApplicationDep: TypeAlias = Annotated[
    AccountApplication, Depends(get_account_application)
]

# Company Application
CompanyApplicationDep: TypeAlias = Annotated[
    CompanyApplication, Depends(get_company_application)
]

# Location Application
LocationApplicationDep: TypeAlias = Annotated[
    LocationApplication, Depends(get_location_application)
]

# Menu Application
MenuApplicationDep: TypeAlias = Annotated[
    MenuApplication, Depends(get_menu_application)
]
