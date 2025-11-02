import base64
from typing import AsyncGenerator

import httpx
import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.account.models import User
from src.backoffice.apps.account.utils import get_password_hash
from src.backoffice.apps.company.models import Company, CompanyMember
from src.backoffice.apps.company.models.types import (
    CompanyEstablishmentType,
    CompanyRole,
    CuisineCategory,
)
from src.backoffice.core.app import create_app
from src.backoffice.core.dependencies.database import get_session


@pytest_asyncio.fixture
async def test_user(test_session: AsyncSession) -> User:
    password = "test_password_123"
    password_hash = get_password_hash(password)
    user = User(
        email="test@example.com",
        password_hash=password_hash,
        is_active=True,
        is_verified=True,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_app(test_session: AsyncSession):
    app = create_app()

    async def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session

    yield app

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(test_app) -> AsyncGenerator[httpx.AsyncClient, None]:
    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def create_basic_auth_header(email: str, password: str) -> str:
    credentials = f"{email}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


@pytest.mark.asyncio
async def test_create_company_endpoint_success(
    client: httpx.AsyncClient, test_user: User, test_session: AsyncSession
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
    test_user: User,
    test_session: AsyncSession,
):
    existing_company = Company(
        name="Existing Restaurant",
        description="Existing",
        subdomain="existing-restaurant",
        type_of_establishment=CompanyEstablishmentType.RESTAURANT,
        cuisine_category=CuisineCategory.JAPANESE,
    )
    test_session.add(existing_company)
    await test_session.commit()

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
    client: httpx.AsyncClient, test_user: User
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
