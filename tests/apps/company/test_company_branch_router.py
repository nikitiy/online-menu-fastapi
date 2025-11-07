from unittest.mock import AsyncMock, patch

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.company.models import CompanyBranch
from src.backoffice.apps.company.models.types import CompanyRole
from src.backoffice.apps.company.repositories import CompanyMemberRepository
from tests.fixtures.companies import company_with_member, test_company
from tests.fixtures.factories import CompanyBranchFactory, CompanyFactory, UserFactory
from tests.utils.auth import create_basic_auth_header


@pytest.mark.asyncio
async def test_create_company_branch_success(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
    company_with_member,
):
    company, _ = company_with_member

    branch_data = {
        "company_id": company.id,
        "name": "Main Branch",
        "description": "Main branch description",
        "latitude": 55.7558,
        "longitude": 37.6173,
        "phone": "+7-999-123-45-67",
        "email": "branch@example.com",
    }

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    with patch(
        "src.backoffice.apps.company.application.QRCodeService.create_qr_code_for_branch",
        new_callable=AsyncMock,
    ):
        response = await client.post(
            "/api/v1/company-branches/",
            json=branch_data,
            headers={"Authorization": auth_header},
        )

    assert response.status_code == 201
    data = response.json()

    assert data["name"] == "Main Branch"
    assert data["description"] == "Main branch description"
    assert data["company_id"] == company.id
    assert data["latitude"] == 55.7558
    assert data["longitude"] == 37.6173
    assert data["phone"] == "+7-999-123-45-67"
    assert data["email"] == "branch@example.com"
    assert "id" not in data
    assert "created_at" not in data
    assert "updated_at" not in data

    result = await test_session.execute(
        select(CompanyBranch).where(
            CompanyBranch.company_id == company.id, CompanyBranch.name == "Main Branch"
        )
    )
    created_branch = result.scalar_one_or_none()
    assert created_branch is not None
    assert created_branch.name == "Main Branch"


@pytest.mark.asyncio
async def test_create_company_branch_unauthorized(
    client: httpx.AsyncClient, test_session: AsyncSession, test_company
):
    branch_data = {
        "company_id": test_company.id,
        "name": "Main Branch",
    }

    response = await client.post("/api/v1/company-branches/", json=branch_data)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_company_branch_forbidden(
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

    branch_data = {
        "company_id": company.id,
        "name": "Main Branch",
    }

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.post(
        "/api/v1/company-branches/",
        json=branch_data,
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 403
    assert (
        "permission" in response.json()["detail"].lower()
        or "member" in response.json()["detail"].lower()
    )


@pytest.mark.asyncio
async def test_create_company_branch_viewer_forbidden(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
    company_with_member,
):
    company, member = company_with_member

    member_repo = CompanyMemberRepository(test_session)
    await member_repo.update(member.id, role=CompanyRole.VIEWER)
    await test_session.commit()

    branch_data = {
        "company_id": company.id,
        "name": "Main Branch",
    }

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.post(
        "/api/v1/company-branches/",
        json=branch_data,
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_company_branch_success(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
    company_with_member,
):
    company, _ = company_with_member

    branch = await CompanyBranchFactory.create(
        session=test_session,
        company_id=company.id,
        name="Test Branch",
        description="Test description",
    )

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.get(
        f"/api/v1/company-branches/{branch.id}",
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "Test Branch"
    assert data["description"] == "Test description"
    assert data["company_id"] == company.id
    assert "id" not in data
    assert "created_at" not in data
    assert "updated_at" not in data


@pytest.mark.asyncio
async def test_get_company_branch_not_found(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
    company_with_member,
):
    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.get(
        "/api/v1/company-branches/99999",
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_company_branch_forbidden(
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

    branch = await CompanyBranchFactory.create(
        session=test_session,
        company_id=company.id,
        name="Other Branch",
    )

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.get(
        f"/api/v1/company-branches/{branch.id}",
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_company_branches_success(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
    company_with_member,
):
    company, _ = company_with_member

    await CompanyBranchFactory.create(
        session=test_session,
        company_id=company.id,
        name="Branch 1",
    )
    await CompanyBranchFactory.create(
        session=test_session,
        company_id=company.id,
        name="Branch 2",
    )

    other_company = await CompanyFactory.create(
        session=test_session,
        name="Other Company",
        subdomain="other-company",
    )
    await CompanyBranchFactory.create(
        session=test_session,
        company_id=other_company.id,
        name="Other Branch",
    )

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.get(
        "/api/v1/company-branches/",
        params={"company_id": company.id},
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    branch_names = {b["name"] for b in data}
    assert "Branch 1" in branch_names
    assert "Branch 2" in branch_names


@pytest.mark.asyncio
async def test_list_company_branches_empty(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
    company_with_member,
):
    company, _ = company_with_member

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.get(
        "/api/v1/company-branches/",
        params={"company_id": company.id},
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 0


@pytest.mark.asyncio
async def test_list_company_branches_forbidden(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
):
    other_company = await CompanyFactory.create(
        session=test_session,
        name="Other Company",
        subdomain="other-company",
    )

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.get(
        "/api/v1/company-branches/",
        params={"company_id": other_company.id},
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_company_branch_success(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
    company_with_member,
):
    company, _ = company_with_member

    branch = await CompanyBranchFactory.create(
        session=test_session,
        company_id=company.id,
        name="Original Name",
        description="Original description",
    )

    update_data = {
        "name": "Updated Name",
        "description": "Updated description",
        "is_active": False,
        "is_verified": True,
    }

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.put(
        f"/api/v1/company-branches/{branch.id}",
        json=update_data,
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "Updated Name"
    assert data["description"] == "Updated description"
    assert data["is_active"] is False
    assert data["is_verified"] is True


@pytest.mark.asyncio
async def test_update_company_branch_partial(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
    company_with_member,
):
    company, _ = company_with_member

    branch = await CompanyBranchFactory.create(
        session=test_session,
        company_id=company.id,
        name="Original Name",
        description="Original description",
        phone="+7-999-111-11-11",
    )

    update_data = {"name": "Updated Name"}

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.put(
        f"/api/v1/company-branches/{branch.id}",
        json=update_data,
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "Updated Name"
    assert data["description"] == "Original description"
    assert data["phone"] == "+7-999-111-11-11"


@pytest.mark.asyncio
async def test_update_company_branch_forbidden(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
    company_with_member,
):
    company, member = company_with_member

    member_repo = CompanyMemberRepository(test_session)
    await member_repo.update(member.id, role=CompanyRole.VIEWER)
    await test_session.commit()

    branch = await CompanyBranchFactory.create(
        session=test_session,
        company_id=company.id,
        name="Test Branch",
    )

    update_data = {"name": "Updated Name"}

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.put(
        f"/api/v1/company-branches/{branch.id}",
        json=update_data,
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_company_branch_success(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
    company_with_member,
):
    company, _ = company_with_member

    branch = await CompanyBranchFactory.create(
        session=test_session,
        company_id=company.id,
        name="Branch to Delete",
    )

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.delete(
        f"/api/v1/company-branches/{branch.id}",
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 204

    deleted_branch = await test_session.get(CompanyBranch, branch.id)
    assert deleted_branch is None


@pytest.mark.asyncio
async def test_delete_company_branch_forbidden(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
    company_with_member,
):
    company, member = company_with_member

    member_repo = CompanyMemberRepository(test_session)
    await member_repo.update(member.id, role=CompanyRole.VIEWER)
    await test_session.commit()

    branch = await CompanyBranchFactory.create(
        session=test_session,
        company_id=company.id,
        name="Test Branch",
    )

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.delete(
        f"/api/v1/company-branches/{branch.id}",
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_company_branch_not_found(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
    company_with_member,
):
    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.delete(
        "/api/v1/company-branches/99999",
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 404
