from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.account.models import User
from src.backoffice.apps.company.exceptions import SubdomainAlreadyTaken
from src.backoffice.apps.company.models import Company, CompanyMember
from src.backoffice.apps.company.models.types import (
    CompanyEstablishmentType,
    CompanyRole,
    CuisineCategory,
)
from src.backoffice.apps.company.schemas import CompanyCreate
from src.backoffice.apps.company.services import CompanyService


@pytest_asyncio.fixture
async def company_service(test_session: AsyncSession) -> CompanyService:
    return CompanyService(test_session)


@pytest_asyncio.fixture
async def sample_company(
    company_service: CompanyService,
) -> Company:
    company_data = CompanyCreate(
        name="Test Restaurant",
        description="A test restaurant",
        subdomain="test-restaurant",
        type_of_establishment=CompanyEstablishmentType.RESTAURANT,
        cuisine_category=CuisineCategory.JAPANESE,
    )
    return await company_service.create_company(company_data)


@pytest.mark.asyncio
async def test_create_company_success(company_service: CompanyService):
    company_data = CompanyCreate(
        name="New Restaurant",
        description="A new restaurant",
        subdomain="new-restaurant",
        type_of_establishment=CompanyEstablishmentType.CAFE,
        cuisine_category=CuisineCategory.RUSSIAN,
    )

    company = await company_service.create_company(company_data)

    assert company.id is not None
    assert company.name == "New Restaurant"
    assert company.description == "A new restaurant"
    assert company.subdomain == "new-restaurant"
    assert company.type_of_establishment == CompanyEstablishmentType.CAFE
    assert company.cuisine_category == CuisineCategory.RUSSIAN


@pytest.mark.asyncio
async def test_create_company_subdomain_taken(
    company_service: CompanyService, sample_company: Company
):
    company_data = CompanyCreate(
        name="Another Restaurant",
        description="Another restaurant",
        subdomain=sample_company.subdomain,
        type_of_establishment=CompanyEstablishmentType.RESTAURANT,
        cuisine_category=CuisineCategory.JAPANESE,
    )

    with pytest.raises(SubdomainAlreadyTaken) as exc_info:
        await company_service.create_company(company_data)

    assert sample_company.subdomain in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_company_creates_site(company_service: CompanyService):
    company_data = CompanyCreate(
        name="Restaurant with Site",
        description="A restaurant",
        subdomain="restaurant-site",
        type_of_establishment=CompanyEstablishmentType.RESTAURANT,
        cuisine_category=CuisineCategory.JAPANESE,
    )

    with patch.object(
        company_service.site_service, "create_site", new_callable=AsyncMock
    ) as mock_create_site:
        company = await company_service.create_company(company_data)

        mock_create_site.assert_called_once_with(company.id)
        assert company.id is not None


@pytest.mark.asyncio
async def test_get_accessible_companies_for_user(
    company_service: CompanyService, test_session: AsyncSession
):
    user = User(email="user@example.com", password_hash="hashed_password")
    test_session.add(user)
    await test_session.flush()

    company1_data = CompanyCreate(
        name="Company 1",
        description="First company",
        subdomain="company1",
        type_of_establishment=CompanyEstablishmentType.RESTAURANT,
        cuisine_category=CuisineCategory.JAPANESE,
    )

    company2_data = CompanyCreate(
        name="Company 2",
        description="Second company",
        subdomain="company2",
        type_of_establishment=CompanyEstablishmentType.CAFE,
        cuisine_category=CuisineCategory.RUSSIAN,
    )

    company1 = await company_service.create_company(company1_data)
    company2 = await company_service.create_company(company2_data)

    company3_data = CompanyCreate(
        name="Company 3",
        description="Third company",
        subdomain="company3",
        type_of_establishment=CompanyEstablishmentType.BAR,
        cuisine_category=CuisineCategory.OTHER,
    )
    company3 = await company_service.create_company(company3_data)

    member1 = CompanyMember(
        company_id=company1.id, user_id=user.id, role=CompanyRole.OWNER
    )
    member2 = CompanyMember(
        company_id=company2.id, user_id=user.id, role=CompanyRole.ADMIN
    )
    test_session.add_all([member1, member2])
    await test_session.flush()

    companies = await company_service.get_accessible_companies_for_user(user.id)

    assert len(companies) == 2
    company_ids = {c.id for c in companies}
    assert company1.id in company_ids
    assert company2.id in company_ids
    assert company3.id not in company_ids


@pytest.mark.asyncio
async def test_get_accessible_companies_for_user_empty(
    company_service: CompanyService,
):
    companies = await company_service.get_accessible_companies_for_user(99999)

    assert len(companies) == 0
