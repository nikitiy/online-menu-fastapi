from typing import Annotated, TypeAlias

from fastapi import Depends

from src.backoffice.apps.account.application import AccountApplication
from src.backoffice.apps.account.services.auth_service import (
    AuthService, get_auth_service)
from src.backoffice.apps.account.services.oauth_service import (
    GoogleOAuthService, VKOAuthService, YandexOAuthService)
from src.backoffice.apps.company.application import CompanyApplication
from src.backoffice.apps.location.application import LocationApplication
from src.backoffice.apps.location.services.geocoder_service import \
    GeocoderService
from src.backoffice.apps.location.services.location_service import \
    LocationService
from src.backoffice.apps.menu.application import MenuApplication
from src.backoffice.apps.menu.services.menu_item_service import MenuItemService

from .database import SessionDep

# ==================== SERVICE DEPENDENCIES ====================


async def get_account_application(session: SessionDep) -> AccountApplication:
    return AccountApplication(session)


async def get_company_application(session: SessionDep) -> CompanyApplication:
    return CompanyApplication(session)


async def get_location_application(session: SessionDep) -> LocationApplication:
    return LocationApplication(session)


async def get_geocoder_service(session: SessionDep) -> GeocoderService:
    return GeocoderService(session)


async def get_location_service(session: SessionDep) -> LocationService:
    return LocationService(session)


async def get_menu_application(session: SessionDep) -> MenuApplication:
    return MenuApplication(session)


async def get_menu_item_service(session: SessionDep) -> MenuItemService:
    return MenuItemService(session)


# OAuth Services
async def get_google_oauth_service() -> GoogleOAuthService:
    return GoogleOAuthService()


async def get_yandex_oauth_service() -> YandexOAuthService:
    return YandexOAuthService()


async def get_vk_oauth_service() -> VKOAuthService:
    return VKOAuthService()


# ==================== ANNOTATED TYPES ====================

# Account Application
AccountApplicationDep: TypeAlias = Annotated[
    AccountApplication, Depends(get_account_application)
]

# Auth Service
AuthServiceDep: TypeAlias = Annotated[AuthService, Depends(get_auth_service)]

# Company Application
CompanyApplicationDep: TypeAlias = Annotated[
    CompanyApplication, Depends(get_company_application)
]

# Location Application
LocationApplicationDep: TypeAlias = Annotated[
    LocationApplication, Depends(get_location_application)
]

# Geocoder Service (deprecated, use LocationApplicationDep)
GeocoderServiceDep: TypeAlias = Annotated[
    GeocoderService, Depends(get_geocoder_service)
]

# Location Service (deprecated, use LocationApplicationDep)
LocationServiceDep: TypeAlias = Annotated[
    LocationService, Depends(get_location_service)
]

# Menu Application
MenuApplicationDep: TypeAlias = Annotated[
    MenuApplication, Depends(get_menu_application)
]

# Menu Item Service
MenuItemServiceDep: TypeAlias = Annotated[
    MenuItemService, Depends(get_menu_item_service)
]

# OAuth Services
GoogleOAuthServiceDep: TypeAlias = Annotated[
    GoogleOAuthService, Depends(get_google_oauth_service)
]
YandexOAuthServiceDep: TypeAlias = Annotated[
    YandexOAuthService, Depends(get_yandex_oauth_service)
]
VKOAuthServiceDep: TypeAlias = Annotated[
    VKOAuthService, Depends(get_vk_oauth_service)
]  # TODO в этом файле много зависимостей не нужны и нигде не используются
