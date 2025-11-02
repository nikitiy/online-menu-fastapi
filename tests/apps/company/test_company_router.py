import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.company.models import Company, CompanyMember
from src.backoffice.apps.company.models.types import (
    CompanyEstablishmentType,
    CompanyRole,
    CuisineCategory,
)
from tests.fixtures.factories import CompanyFactory
from tests.utils.auth import create_basic_auth_header


@pytest.mark.asyncio
async def test_create_company_endpoint_success(
    client: httpx.AsyncClient, test_user, test_session: AsyncSession
):
    company_data = {
        "name": "New Restaurant",
        "description": "A new restaurant",
        "subdomain": "new-restaurant",
        "type_of_establishment": CompanyEstablishmentType.CAFE.value,
        "cuisine_category": CuisineCategory.RUSSIAN.value,
    }

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")
    response = await client.post(
        "/api/v1/companies/",
        json=company_data,
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 201
    data = response.json()

    assert data["name"] == "New Restaurant"
    assert data["description"] == "A new restaurant"
    assert data["subdomain"] == "new-restaurant"
    assert data["type_of_establishment"] == CompanyEstablishmentType.CAFE.value
    assert data["cuisine_category"] == CuisineCategory.RUSSIAN.value
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

    await test_session.refresh(test_user)
    created_company = await test_session.get(Company, data["id"])
    assert created_company is not None
    assert created_company.name == "New Restaurant"
    assert created_company.subdomain == "new-restaurant"

    result = await test_session.execute(
        select(CompanyMember).where(
            CompanyMember.company_id == data["id"],
            CompanyMember.user_id == test_user.id,
        )
    )
    member = result.scalar_one_or_none()
    assert member is not None
    assert member.role == CompanyRole.OWNER


@pytest.mark.asyncio
async def test_create_company_endpoint_unauthorized(client: httpx.AsyncClient):
    company_data = {
        "name": "New Restaurant",
        "subdomain": "new-restaurant",
        "type_of_establishment": CompanyEstablishmentType.CAFE.value,
        "cuisine_category": CuisineCategory.RUSSIAN.value,
    }

    response = await client.post("/api/v1/companies/", json=company_data)

    assert response.status_code == 401
    assert (
        "Authentication required" in response.json()["detail"]
        or "detail" in response.json()
    )


@pytest.mark.asyncio
async def test_create_company_endpoint_subdomain_taken(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
):
    await CompanyFactory.create(
        session=test_session,
        name="Existing Restaurant",
        description="Existing",
        subdomain="existing-restaurant",
        type_of_establishment=CompanyEstablishmentType.RESTAURANT,
        cuisine_category=CuisineCategory.JAPANESE,
    )

    company_data = {
        "name": "New Restaurant",
        "subdomain": "existing-restaurant",
        "type_of_establishment": CompanyEstablishmentType.CAFE.value,
        "cuisine_category": CuisineCategory.RUSSIAN.value,
    }

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")
    response = await client.post(
        "/api/v1/companies/",
        json=company_data,
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 409
    assert (
        "subdomain" in response.json()["detail"].lower()
        or "already" in response.json()["detail"].lower()
    )


@pytest.mark.asyncio
async def test_create_company_endpoint_invalid_data(
    client: httpx.AsyncClient, test_user
):
    company_data = {
        "name": "",
        "subdomain": "invalid-subdomain!!!",
        "type_of_establishment": CompanyEstablishmentType.CAFE.value,
        "cuisine_category": CuisineCategory.RUSSIAN.value,
    }

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")
    response = await client.post(
        "/api/v1/companies/",
        json=company_data,
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 422
