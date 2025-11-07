from fastapi import APIRouter

from src.backoffice.api.v1.auth import auth_router
from src.backoffice.api.v1.company import company_branch_router, company_router

# from src.backoffice.api.v1.location import geocoding_router, location_router
from src.backoffice.api.v1.menu import menu_item_router
from src.backoffice.api.v1.qr_manager import qr_code_router

api_router = APIRouter()

# Auth routes
api_router.include_router(auth_router)

# Location routes
# api_router.include_router(geocoding_router, prefix="/location")
# api_router.include_router(location_router, prefix="/location")

# Menu routes
api_router.include_router(menu_item_router)

# Company routes
api_router.include_router(company_router)
api_router.include_router(company_branch_router)

# QR Code routes
api_router.include_router(qr_code_router)

__all__ = ("api_router",)
