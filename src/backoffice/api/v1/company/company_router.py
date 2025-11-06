from typing import List

from fastapi import APIRouter, status

from src.backoffice.apps.company.schemas import (
    CompanyCreate,
    CompanyMemberCreateByEmail,
    CompanyMemberCreateByEmailResponse,
    CompanyMemberResponse,
    CompanyMemberUpdateByEmail,
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


@router.post(
    "/{company_subdomain}/members/by-email",
    response_model=CompanyMemberCreateByEmailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add company member by email",
)
async def add_member_by_email(
    company_subdomain: str,
    member_data: CompanyMemberCreateByEmail,
    request_user: AuthenticatedUserDep,
    application: CompanyApplicationDep,
):
    return await application.add_member_by_email(
        company_subdomain, member_data, request_user.id
    )


@router.delete(
    "/{company_subdomain}/members/by-email",  # TODO думаю тут лучше не делать by-email а просто /members
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove company member by email",
)
async def remove_member_by_email(
    company_subdomain: str,
    user_email: str,
    request_user: AuthenticatedUserDep,
    application: CompanyApplicationDep,
):
    await application.remove_member_by_email(
        company_subdomain, user_email, request_user.id
    )


@router.patch(
    "/{company_subdomain}/members/by-email",
    response_model=CompanyMemberResponse,
    summary="Update company member role by email",
)
async def update_member_role_by_email(
    company_subdomain: str,
    member_data: CompanyMemberUpdateByEmail,
    request_user: AuthenticatedUserDep,
    application: CompanyApplicationDep,
):
    return await application.update_member_role_by_email(
        company_subdomain, member_data, request_user.id
    )
