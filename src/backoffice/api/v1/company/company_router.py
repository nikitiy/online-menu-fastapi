from typing import List

from fastapi import APIRouter, status

from src.backoffice.apps.company.schemas import (
    CompanyCreate,
    CompanyResponse,
    CompanyShortResponse,
)
from src.backoffice.core.dependencies import AuthenticatedUserDep, CompanyApplicationDep

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post(
    "/",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create company",
)
async def create_company(
    company_data: CompanyCreate,
    request_user: AuthenticatedUserDep,
    application: CompanyApplicationDep,
):
    return await application.create_company_with_owner(company_data, request_user.id)


@router.get(
    "/",
    response_model=List[CompanyShortResponse],
    summary="List companies accessible to user",
)
async def list_user_companies(
    request_user: AuthenticatedUserDep, application: CompanyApplicationDep
):
    return await application.get_accessible_companies_for_user(request_user.id)
