import hashlib

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.company.models.types import CompanyRole
from src.backoffice.apps.company.repositories import CompanyMemberRepository
from tests.fixtures.companies import company_with_member, test_company
from tests.fixtures.factories import (
    CompanyBranchFactory,
    CompanyFactory,
    QRCodeFactory,
    UserFactory,
)
from tests.utils.auth import create_basic_auth_header


@pytest.mark.asyncio
async def test_get_qr_code_by_branch_success(
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
    )

    url_hash = hashlib.sha256(f"http://test/branch/{branch.id}".encode()).hexdigest()
    await QRCodeFactory.create(
        session=test_session,
        company_branch_id=branch.id,
        url_hash=url_hash,
        qr_options={"version": 1, "box_size": 10},
    )

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.get(
        f"/api/v1/qr-codes/branch/{branch.id}",
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["company_branch_id"] == branch.id
    assert data["url_hash"] == url_hash
    assert data["qr_options"] == {"version": 1, "box_size": 10}
    assert data["scan_count"] == 0
    assert "id" not in data
    assert "created_at" not in data
    assert "updated_at" not in data


@pytest.mark.asyncio
async def test_get_qr_code_by_branch_not_found(
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
    )

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.get(
        f"/api/v1/qr-codes/branch/{branch.id}",
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_qr_code_by_branch_unauthorized(
    client: httpx.AsyncClient,
    test_session: AsyncSession,
    test_company,
):
    branch = await CompanyBranchFactory.create(
        session=test_session,
        company_id=test_company.id,
        name="Test Branch",
    )

    response = await client.get(f"/api/v1/qr-codes/branch/{branch.id}")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_qr_code_by_branch_forbidden(
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

    url_hash = hashlib.sha256(f"http://test/branch/{branch.id}".encode()).hexdigest()
    await QRCodeFactory.create(
        session=test_session,
        company_branch_id=branch.id,
        url_hash=url_hash,
    )

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.get(
        f"/api/v1/qr-codes/branch/{branch.id}",
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_qr_code_by_branch_viewer_allowed(
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

    url_hash = hashlib.sha256(f"http://test/branch/{branch.id}".encode()).hexdigest()
    await QRCodeFactory.create(
        session=test_session,
        company_branch_id=branch.id,
        url_hash=url_hash,
        qr_options={"version": 1},
    )

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.get(
        f"/api/v1/qr-codes/branch/{branch.id}",
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["url_hash"] == url_hash


@pytest.mark.asyncio
async def test_get_qr_code_image_success(
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
    )

    url_hash = hashlib.sha256(f"http://test/branch/{branch.id}".encode()).hexdigest()
    await QRCodeFactory.create(
        session=test_session,
        company_branch_id=branch.id,
        url_hash=url_hash,
    )

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.get(
        f"/api/v1/qr-codes/branch/{branch.id}/image",
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert len(response.content) > 0
    assert response.content.startswith(b"\x89PNG")


@pytest.mark.asyncio
async def test_get_qr_code_image_not_found(
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
    )

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.get(
        f"/api/v1/qr-codes/branch/{branch.id}/image",
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_qr_code_image_unauthorized(
    client: httpx.AsyncClient,
    test_session: AsyncSession,
    test_company,
):
    branch = await CompanyBranchFactory.create(
        session=test_session,
        company_id=test_company.id,
        name="Test Branch",
    )

    response = await client.get(f"/api/v1/qr-codes/branch/{branch.id}/image")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_qr_code_image_forbidden(
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

    url_hash = hashlib.sha256(f"http://test/branch/{branch.id}".encode()).hexdigest()
    await QRCodeFactory.create(
        session=test_session,
        company_branch_id=branch.id,
        url_hash=url_hash,
    )

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.get(
        f"/api/v1/qr-codes/branch/{branch.id}/image",
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_qr_code_success(
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
    )

    url_hash = hashlib.sha256(f"http://test/branch/{branch.id}".encode()).hexdigest()
    await QRCodeFactory.create(
        session=test_session,
        company_branch_id=branch.id,
        url_hash=url_hash,
        qr_options={"version": 1},
    )

    update_data = {"qr_options": {"version": 2, "box_size": 15, "fill_color": "blue"}}

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.put(
        f"/api/v1/qr-codes/{url_hash}",
        json=update_data,
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["url_hash"] == url_hash
    assert data["qr_options"] == {"version": 2, "box_size": 15, "fill_color": "blue"}
    assert "id" not in data
    assert "created_at" not in data
    assert "updated_at" not in data


@pytest.mark.asyncio
async def test_update_qr_code_partial(
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
    )

    url_hash = hashlib.sha256(f"http://test/branch/{branch.id}".encode()).hexdigest()
    await QRCodeFactory.create(
        session=test_session,
        company_branch_id=branch.id,
        url_hash=url_hash,
        qr_options={"version": 1, "box_size": 10},
    )

    update_data = {"qr_options": {"version": 2}}

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.put(
        f"/api/v1/qr-codes/{url_hash}",
        json=update_data,
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["qr_options"] == {"version": 2, "box_size": 10}


@pytest.mark.asyncio
async def test_update_qr_code_empty_update(
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
    )

    url_hash = hashlib.sha256(f"http://test/branch/{branch.id}".encode()).hexdigest()
    await QRCodeFactory.create(
        session=test_session,
        company_branch_id=branch.id,
        url_hash=url_hash,
        qr_options={"version": 1},
    )

    update_data = {}

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.put(
        f"/api/v1/qr-codes/{url_hash}",
        json=update_data,
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["qr_options"] == {"version": 1}


@pytest.mark.asyncio
async def test_update_qr_code_not_found(
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
    company_with_member,
):
    url_hash = hashlib.sha256("http://test/branch/99999".encode()).hexdigest()

    update_data = {"qr_options": {"version": 2}}

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.put(
        f"/api/v1/qr-codes/{url_hash}",
        json=update_data,
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_qr_code_unauthorized(
    client: httpx.AsyncClient,
    test_session: AsyncSession,
):
    url_hash = hashlib.sha256("http://test/branch/1".encode()).hexdigest()

    update_data = {"qr_options": {"version": 2}}

    response = await client.put(
        f"/api/v1/qr-codes/{url_hash}",
        json=update_data,
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_qr_code_forbidden(
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

    url_hash = hashlib.sha256(f"http://test/branch/{branch.id}".encode()).hexdigest()
    await QRCodeFactory.create(
        session=test_session,
        company_branch_id=branch.id,
        url_hash=url_hash,
    )

    update_data = {"qr_options": {"version": 2}}

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.put(
        f"/api/v1/qr-codes/{url_hash}",
        json=update_data,
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_qr_code_viewer_forbidden(
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

    url_hash = hashlib.sha256(f"http://test/branch/{branch.id}".encode()).hexdigest()
    await QRCodeFactory.create(
        session=test_session,
        company_branch_id=branch.id,
        url_hash=url_hash,
    )

    update_data = {"qr_options": {"version": 2}}

    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.put(
        f"/api/v1/qr-codes/{url_hash}",
        json=update_data,
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 403
