from typing import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.company.models.types import (
    CompanyEstablishmentType,
    CompanyRole,
    CuisineCategory,
)
from src.backoffice.apps.company.schemas import CompanyCreate
from src.backoffice.apps.company.services import (
    CompanyBranchService,
    CompanyMemberService,
    CompanyService,
)
from tests.fixtures.factories import CompanyFactory, CompanyMemberFactory


@pytest_asyncio.fixture
async def company_service(test_session: AsyncSession) -> CompanyService:
    return CompanyService(test_session)


@pytest_asyncio.fixture
async def company_branch_service(test_session: AsyncSession) -> CompanyBranchService:
    return CompanyBranchService(test_session)


@pytest_asyncio.fixture
async def company_member_service(test_session: AsyncSession) -> CompanyMemberService:
    return CompanyMemberService(test_session)


@pytest_asyncio.fixture
async def sample_company(
    company_service: CompanyService,
) -> AsyncGenerator:
    company_data = CompanyCreate(
        name="Test Restaurant",
        description="A test restaurant",
        subdomain="test-restaurant",
        type_of_establishment=CompanyEstablishmentType.RESTAURANT,
        cuisine_category=CuisineCategory.JAPANESE,
    )
    company = await company_service.create_company(company_data)
    yield company


@pytest_asyncio.fixture
async def test_company(test_session: AsyncSession) -> AsyncGenerator:
    company = await CompanyFactory.create(
        session=test_session,
        name="Test Restaurant",
        description="A test restaurant",
        subdomain="test-restaurant",
        type_of_establishment=CompanyEstablishmentType.RESTAURANT,
        cuisine_category=CuisineCategory.JAPANESE,
    )
    yield company


@pytest_asyncio.fixture
async def company_with_member(test_user, test_session: AsyncSession) -> AsyncGenerator:
    company = await CompanyFactory.create(
        session=test_session,
        name="User's Restaurant",
        subdomain="user-restaurant",
    )
    member = await CompanyMemberFactory.create(
        session=test_session,
        company_id=company.id,
        user_id=test_user.id,
        role=CompanyRole.OWNER,
    )
    yield company, member
