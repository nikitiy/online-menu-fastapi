from typing import List

from fastapi import APIRouter, status

from src.backoffice.apps.company.schemas import (
    CompanyBranchCreate,
    CompanyBranchResponse,
    CompanyBranchUpdate,
)
from src.backoffice.core.dependencies import AuthenticatedUserDep, CompanyApplicationDep

router = APIRouter(prefix="/company-branches", tags=["company-branches"])


@router.post(
    "/",
    response_model=CompanyBranchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create company branch",
)
async def create_company_branch(
    branch_data: CompanyBranchCreate,
    request_user: AuthenticatedUserDep,
    application: CompanyApplicationDep,
):
    """Create a new company branch"""
    return await application.create_branch(branch_data, request_user.id)


@router.get(
    "/{branch_id}",
    response_model=CompanyBranchResponse,
    summary="Get company branch by ID",
)
async def get_company_branch(
    branch_id: int,
    request_user: AuthenticatedUserDep,
    application: CompanyApplicationDep,
):
    """Get company branch by ID"""
    return await application.get_branch_by_id(branch_id, request_user.id)


@router.get(
    "/",
    response_model=List[CompanyBranchResponse],
    summary="Get company branches",
)
async def list_company_branches(
    company_id: int,
    request_user: AuthenticatedUserDep,
    application: CompanyApplicationDep,
):
    """Get all branches for a company"""
    return await application.get_branches_by_company(company_id, request_user.id)


@router.put(
    "/{branch_id}",
    response_model=CompanyBranchResponse,
    summary="Update company branch",
)
async def update_company_branch(
    branch_id: int,
    branch_data: CompanyBranchUpdate,
    request_user: AuthenticatedUserDep,
    application: CompanyApplicationDep,
):
    """Update company branch"""
    return await application.update_branch(branch_id, branch_data, request_user.id)


@router.delete(
    "/{branch_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete company branch",
)
async def delete_company_branch(
    branch_id: int,
    request_user: AuthenticatedUserDep,
    application: CompanyApplicationDep,
):
    """Delete company branch"""
    await application.delete_branch(branch_id, request_user.id)
