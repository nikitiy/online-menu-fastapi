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
from tests.fixtures.factories import CompanyFactory, CompanyMemberFactory, UserFactory
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


@pytest.mark.asyncio
async def test_list_user_companies_success(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
):
    company1 = await CompanyFactory.create(
        session=test_session,
        name="Company 1",
        subdomain="company1",
    )
    company2 = await CompanyFactory.create(
        session=test_session,
        name="Company 2",
        subdomain="company2",
    )
    company3 = await CompanyFactory.create(
        session=test_session,
        name="Company 3",
        subdomain="company3",
    )

    await CompanyMemberFactory.create(
        session=test_session,
        company_id=company1.id,
        user_id=test_user.id,
        role=CompanyRole.OWNER,
        commit=False,
    )
    await CompanyMemberFactory.create(
        session=test_session,
        company_id=company2.id,
        user_id=test_user.id,
        role=CompanyRole.ADMIN,
        commit=False,
    )
    await test_session.commit()

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")
    response = await client.get(
        "/api/v1/companies/",
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    company_subdomains = {c["subdomain"] for c in data}
    assert company1.subdomain in company_subdomains
    assert company2.subdomain in company_subdomains
    assert company3.subdomain not in company_subdomains


@pytest.mark.asyncio
async def test_list_user_companies_empty(
    client: httpx.AsyncClient,
    test_user,
):
    auth_header = create_basic_auth_header(test_user.email, "test_password_123")
    response = await client.get(
        "/api/v1/companies/",
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 0


@pytest.mark.asyncio
async def test_list_user_companies_unauthorized(client: httpx.AsyncClient):
    response = await client.get("/api/v1/companies/")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_add_member_by_email_success(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
    company_with_member,
):
    company, _ = company_with_member

    new_user = await UserFactory.create(
        session=test_session,
        email="newmember@example.com",
        password="password",
    )

    member_data = {"user_email": new_user.email}

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")
    response = await client.post(
        f"/api/v1/companies/{company.subdomain}/members/by-email",
        json=member_data,
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 201
    data = response.json()

    assert "message" in data
    assert "company_member" in data
    assert data["company_member"]["user_id"] == new_user.id
    assert data["company_member"]["company_id"] == company.id
    assert data["company_member"]["role"] == CompanyRole.VIEWER.value


@pytest.mark.asyncio
async def test_add_member_by_email_unauthorized(
    client: httpx.AsyncClient,
    test_session: AsyncSession,
    company_with_member,
):
    company, _ = company_with_member

    new_user = await UserFactory.create(
        session=test_session,
        email="newmember@example.com",
        password="password",
    )

    member_data = {"user_email": new_user.email}

    response = await client.post(
        f"/api/v1/companies/{company.subdomain}/members/by-email",
        json=member_data,
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_add_member_by_email_forbidden(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
):
    await UserFactory.create(
        session=test_session,
        email="other@example.com",
        password="password",
    )
    company = await CompanyFactory.create(
        session=test_session,
        name="Other Company",
        subdomain="other-company",
    )

    new_user = await UserFactory.create(
        session=test_session,
        email="newmember@example.com",
        password="password",
    )

    member_data = {"user_email": new_user.email}

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")
    response = await client.post(
        f"/api/v1/companies/{company.subdomain}/members/by-email",
        json=member_data,
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_add_member_by_email_user_not_found(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
    company_with_member,
):
    company, _ = company_with_member

    member_data = {"user_email": "nonexistent@example.com"}

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")
    response = await client.post(
        f"/api/v1/companies/{company.subdomain}/members/by-email",
        json=member_data,
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 404
    assert "user" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_add_member_by_email_already_member(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
    company_with_member,
):
    company, _ = company_with_member

    existing_user = await UserFactory.create(
        session=test_session,
        email="existing@example.com",
        password="password",
    )

    await CompanyMemberFactory.create(
        session=test_session,
        company_id=company.id,
        user_id=existing_user.id,
        role=CompanyRole.VIEWER,
        commit=False,
    )
    await test_session.commit()

    member_data = {"user_email": existing_user.email}

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")
    response = await client.post(
        f"/api/v1/companies/{company.subdomain}/members/by-email",
        json=member_data,
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 400
    assert "already" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_remove_member_by_email_success(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
    company_with_member,
):
    company, _ = company_with_member

    member_user = await UserFactory.create(
        session=test_session,
        email="member@example.com",
        password="password",
    )

    await CompanyMemberFactory.create(
        session=test_session,
        company_id=company.id,
        user_id=member_user.id,
        role=CompanyRole.VIEWER,
        commit=False,
    )
    await test_session.commit()

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")
    response = await client.delete(
        f"/api/v1/companies/{company.subdomain}/members/by-email",
        params={"user_email": member_user.email},
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_remove_member_by_email_unauthorized(
    client: httpx.AsyncClient,
    test_session: AsyncSession,
    company_with_member,
):
    company, _ = company_with_member

    member_user = await UserFactory.create(
        session=test_session,
        email="member@example.com",
        password="password",
    )

    await CompanyMemberFactory.create(
        session=test_session,
        company_id=company.id,
        user_id=member_user.id,
        role=CompanyRole.VIEWER,
        commit=False,
    )
    await test_session.commit()

    response = await client.delete(
        f"/api/v1/companies/{company.subdomain}/members/by-email",
        params={"user_email": member_user.email},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_remove_member_by_email_forbidden(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
):
    await UserFactory.create(
        session=test_session,
        email="other@example.com",
        password="password",
    )
    company = await CompanyFactory.create(
        session=test_session,
        name="Other Company",
        subdomain="other-company",
    )

    member_user = await UserFactory.create(
        session=test_session,
        email="member@example.com",
        password="password",
    )

    await CompanyMemberFactory.create(
        session=test_session,
        company_id=company.id,
        user_id=member_user.id,
        role=CompanyRole.VIEWER,
        commit=False,
    )
    await test_session.commit()

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")
    response = await client.delete(
        f"/api/v1/companies/{company.subdomain}/members/by-email",
        params={"user_email": member_user.email},
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_remove_member_by_email_owner(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
    company_with_member,
):
    company, _ = company_with_member

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")
    response = await client.delete(
        f"/api/v1/companies/{company.subdomain}/members/by-email",
        params={"user_email": test_user.email},
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 400
    assert "owner" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_remove_member_by_email_user_not_found(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
    company_with_member,
):
    company, _ = company_with_member

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")
    response = await client.delete(
        f"/api/v1/companies/{company.subdomain}/members/by-email",
        params={"user_email": "nonexistent@example.com"},
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_member_role_by_email_success(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
    company_with_member,
):
    company, _ = company_with_member

    member_user = await UserFactory.create(
        session=test_session,
        email="member@example.com",
        password="password",
    )

    await CompanyMemberFactory.create(
        session=test_session,
        company_id=company.id,
        user_id=member_user.id,
        role=CompanyRole.VIEWER,
        commit=False,
    )
    await test_session.commit()

    member_data = {
        "user_email": member_user.email,
        "role": CompanyRole.ADMIN.value,
    }

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")
    response = await client.patch(
        f"/api/v1/companies/{company.subdomain}/members/by-email",
        json=member_data,
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["user_id"] == member_user.id
    assert data["company_id"] == company.id
    assert data["role"] == CompanyRole.ADMIN.value


@pytest.mark.asyncio
async def test_update_member_role_by_email_unauthorized(
    client: httpx.AsyncClient,
    test_session: AsyncSession,
    company_with_member,
):
    company, _ = company_with_member

    member_user = await UserFactory.create(
        session=test_session,
        email="member@example.com",
        password="password",
    )

    await CompanyMemberFactory.create(
        session=test_session,
        company_id=company.id,
        user_id=member_user.id,
        role=CompanyRole.VIEWER,
        commit=False,
    )
    await test_session.commit()

    member_data = {
        "user_email": member_user.email,
        "role": CompanyRole.ADMIN.value,
    }

    response = await client.patch(
        f"/api/v1/companies/{company.subdomain}/members/by-email",
        json=member_data,
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_member_role_by_email_forbidden(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
):
    await UserFactory.create(
        session=test_session,
        email="other@example.com",
        password="password",
    )
    company = await CompanyFactory.create(
        session=test_session,
        name="Other Company",
        subdomain="other-company",
    )

    member_user = await UserFactory.create(
        session=test_session,
        email="member@example.com",
        password="password",
    )

    await CompanyMemberFactory.create(
        session=test_session,
        company_id=company.id,
        user_id=member_user.id,
        role=CompanyRole.VIEWER,
        commit=False,
    )
    await test_session.commit()

    member_data = {
        "user_email": member_user.email,
        "role": CompanyRole.ADMIN.value,
    }

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")
    response = await client.patch(
        f"/api/v1/companies/{company.subdomain}/members/by-email",
        json=member_data,
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_member_role_by_email_owner(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
    company_with_member,
):
    company, _ = company_with_member

    member_data = {
        "user_email": test_user.email,
        "role": CompanyRole.ADMIN.value,
    }

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")
    response = await client.patch(
        f"/api/v1/companies/{company.subdomain}/members/by-email",
        json=member_data,
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 400
    assert "owner" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_member_role_by_email_user_not_found(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
    company_with_member,
):
    company, _ = company_with_member

    member_data = {
        "user_email": "nonexistent@example.com",
        "role": CompanyRole.ADMIN.value,
    }

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")
    response = await client.patch(
        f"/api/v1/companies/{company.subdomain}/members/by-email",
        json=member_data,
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 404
