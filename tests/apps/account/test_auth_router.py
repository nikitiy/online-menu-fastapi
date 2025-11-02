import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.account.models import RefreshToken, User
from tests.fixtures.factories import RefreshTokenFactory, UserFactory
from tests.utils.auth import (
    create_basic_auth_header,
    create_bearer_token,
    create_refresh_token,
)


@pytest.mark.asyncio
async def test_register_user_success(
    test_app_with_account, client: httpx.AsyncClient, test_session: AsyncSession
):
    register_data = {
        "email": "newuser@example.com",
        "password": "password123",
        "username": "newuser",
        "first_name": "New",
        "last_name": "User",
    }

    response = await client.post("/api/v1/auth/register", json=register_data)

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    user = await test_session.execute(
        select(User).where(User.email == "newuser@example.com")
    )
    created_user = user.scalar_one_or_none()
    assert created_user is not None
    assert created_user.email == "newuser@example.com"
    assert created_user.username == "newuser"
    assert created_user.first_name == "New"
    assert created_user.last_name == "User"

    token_result = await test_session.execute(
        select(RefreshToken).where(RefreshToken.user_id == created_user.id)
    )
    refresh_token_obj = token_result.scalar_one_or_none()
    assert refresh_token_obj is not None
    assert refresh_token_obj.token == data["refresh_token"]


@pytest.mark.asyncio
async def test_register_user_duplicate_email(
    test_app_with_account, client: httpx.AsyncClient, test_user
):
    register_data = {
        "email": test_user.email,
        "password": "password123",
    }

    response = await client.post("/api/v1/auth/register", json=register_data)

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_user_duplicate_username(
    test_app_with_account,
    client: httpx.AsyncClient,
    test_session: AsyncSession,
):
    await UserFactory.create(
        session=test_session,
        email="existing@example.com",
        username="existinguser",
        password="password123",
    )

    register_data = {
        "email": "new@example.com",
        "password": "password123",
        "username": "existinguser",
    }

    response = await client.post("/api/v1/auth/register", json=register_data)

    assert response.status_code == 400
    assert "username" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_user_invalid_password(
    test_app_with_account, client: httpx.AsyncClient
):
    register_data = {
        "email": "user@example.com",
        "password": "short",
    }

    response = await client.post("/api/v1/auth/register", json=register_data)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(
    test_app_with_account,
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
):
    login_data = {
        "email": test_user.email,
        "password": "test_password_123",
    }

    response = await client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    token_result = await test_session.execute(
        select(RefreshToken).where(RefreshToken.user_id == test_user.id)
    )
    refresh_token_obj = token_result.scalar_one_or_none()
    assert refresh_token_obj is not None
    assert refresh_token_obj.token == data["refresh_token"]


@pytest.mark.asyncio
async def test_login_invalid_credentials(
    test_app_with_account, client: httpx.AsyncClient, test_user
):
    login_data = {
        "email": test_user.email,
        "password": "wrong_password",
    }

    response = await client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_user_not_found(test_app_with_account, client: httpx.AsyncClient):
    login_data = {
        "email": "nonexistent@example.com",
        "password": "password123",
    }

    response = await client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_inactive_user(
    test_app_with_account, client: httpx.AsyncClient, test_session: AsyncSession
):
    inactive_user = await UserFactory.create(
        session=test_session,
        email="inactive@example.com",
        password="password123",
        is_active=False,
        is_verified=True,
    )

    login_data = {
        "email": inactive_user.email,
        "password": "password123",
    }

    response = await client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 401
    assert "inactive" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_refresh_token_success(
    test_app_with_account,
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
):
    refresh_token_str = create_refresh_token(test_user.id, test_user.email)
    refresh_token_obj = await RefreshTokenFactory.create(
        session=test_session,
        user_id=test_user.id,
        token=refresh_token_str,
    )

    refresh_data = {"refresh_token": refresh_token_str}

    response = await client.post("/api/v1/auth/refresh", json=refresh_data)

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["refresh_token"] != refresh_token_str

    await test_session.commit()
    token_result = await test_session.execute(
        select(RefreshToken).where(RefreshToken.id == refresh_token_obj.id)
    )
    revoked_token = token_result.scalar_one_or_none()
    assert revoked_token is not None
    assert revoked_token.is_revoked is True


@pytest.mark.asyncio
async def test_refresh_token_invalid(test_app_with_account, client: httpx.AsyncClient):
    refresh_data = {"refresh_token": "invalid_token"}

    response = await client.post("/api/v1/auth/refresh", json=refresh_data)

    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_logout_success(
    test_app_with_account,
    client: httpx.AsyncClient,
    test_user,
    test_session: AsyncSession,
):
    refresh_token_str = create_refresh_token(test_user.id, test_user.email)
    refresh_token_obj = await RefreshTokenFactory.create(
        session=test_session,
        user_id=test_user.id,
        token=refresh_token_str,
    )

    refresh_data = {"refresh_token": refresh_token_str}

    response = await client.post("/api/v1/auth/logout", json=refresh_data)

    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"

    await test_session.refresh(refresh_token_obj)
    assert refresh_token_obj.is_revoked is True


@pytest.mark.asyncio
async def test_get_me_with_bearer_token(
    test_app_with_account, client: httpx.AsyncClient, test_user
):
    access_token = create_bearer_token(test_user.id, test_user.email)

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_get_me_with_basic_auth(
    test_app_with_account, client: httpx.AsyncClient, test_user
):
    auth_header = create_basic_auth_header(test_user.email, "test_password_123")

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": auth_header},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == test_user.id
    assert data["email"] == test_user.email


@pytest.mark.asyncio
async def test_get_me_unauthorized(test_app_with_account, client: httpx.AsyncClient):
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert "authentication" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_me_invalid_token(test_app_with_account, client: httpx.AsyncClient):
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_oauth_providers(test_app_with_account, client: httpx.AsyncClient):
    response = await client.get("/api/v1/auth/providers")

    assert response.status_code == 200
    data = response.json()

    assert "providers" in data
    assert isinstance(data["providers"], list)
