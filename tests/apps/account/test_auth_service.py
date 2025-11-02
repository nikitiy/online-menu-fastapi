import pytest
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.account.models import RefreshToken
from src.backoffice.apps.account.schemas import LoginRequest, RegisterRequest
from tests.fixtures.factories import RefreshTokenFactory, UserFactory
from tests.utils.auth import create_refresh_token


@pytest.mark.asyncio
async def test_create_tokens_for_user(
    auth_service, test_user, test_session: AsyncSession
):
    tokens = await auth_service.create_tokens_for_user(test_user)

    assert tokens.access_token is not None
    assert tokens.refresh_token is not None
    assert tokens.token_type == "bearer"

    token_result = await test_session.execute(
        select(RefreshToken).where(RefreshToken.user_id == test_user.id)
    )
    refresh_token_obj = token_result.scalar_one_or_none()
    assert refresh_token_obj is not None
    assert refresh_token_obj.token == tokens.refresh_token


@pytest.mark.asyncio
async def test_register_user_success(auth_service, test_session: AsyncSession):
    register_data = RegisterRequest(
        email="newuser@example.com",
        password="password123",
        username="newuser",
        first_name="New",
        last_name="User",
    )

    tokens, user = await auth_service.register_user(register_data)
    await test_session.commit()

    assert tokens.access_token is not None
    assert tokens.refresh_token is not None
    assert user.email == "newuser@example.com"
    assert user.username == "newuser"
    assert user.first_name == "New"
    assert user.last_name == "User"


@pytest.mark.asyncio
async def test_register_user_duplicate_email(auth_service, test_user):
    register_data = RegisterRequest(email=test_user.email, password="password123")

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.register_user(register_data)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_register_user_duplicate_username(
    auth_service, test_session: AsyncSession
):
    await UserFactory.create(
        session=test_session,
        email="existing@example.com",
        username="existinguser",
        password="password123",
    )

    register_data = RegisterRequest(
        email="new@example.com",
        password="password123",
        username="existinguser",
    )

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.register_user(register_data)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "username" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_authenticate_user_success(
    auth_service, test_user, test_session: AsyncSession
):
    login_data = LoginRequest(email=test_user.email, password="test_password_123")

    tokens, user = await auth_service.authenticate_user(login_data)
    await test_session.commit()

    assert tokens.access_token is not None
    assert tokens.refresh_token is not None
    assert user.id == test_user.id
    assert user.email == test_user.email

    await test_session.refresh(user)
    assert user.last_login is not None


@pytest.mark.asyncio
async def test_authenticate_user_invalid_credentials(auth_service, test_user):
    login_data = LoginRequest(email=test_user.email, password="wrong_password")

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.authenticate_user(login_data)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "incorrect" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_authenticate_user_not_found(auth_service):
    login_data = LoginRequest(email="nonexistent@example.com", password="password123")

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.authenticate_user(login_data)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "incorrect" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_authenticate_user_inactive(auth_service, test_session: AsyncSession):
    inactive_user = await UserFactory.create(
        session=test_session,
        email="inactive@example.com",
        password="password123",
        is_active=False,
        is_verified=True,
    )

    login_data = LoginRequest(email=inactive_user.email, password="password123")

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.authenticate_user(login_data)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "inactive" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_refresh_tokens_success(
    auth_service,
    test_user,
    test_session: AsyncSession,
):
    refresh_token_str = create_refresh_token(test_user.id, test_user.email)
    refresh_token_obj = await RefreshTokenFactory.create(
        session=test_session,
        user_id=test_user.id,
        token=refresh_token_str,
    )

    token_id = refresh_token_obj.id

    new_tokens = await auth_service.refresh_tokens(refresh_token_str)

    assert new_tokens.access_token is not None
    assert new_tokens.refresh_token is not None
    assert new_tokens.refresh_token != refresh_token_str

    token_result = await test_session.execute(
        select(RefreshToken).where(RefreshToken.id == token_id)
    )
    revoked_token = token_result.scalar_one_or_none()
    assert revoked_token is not None
    assert revoked_token.is_revoked is True


@pytest.mark.asyncio
async def test_refresh_tokens_invalid_token(auth_service):
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.refresh_tokens("invalid_token")

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_refresh_tokens_not_in_database(auth_service, test_user):
    refresh_token = create_refresh_token(test_user.id, test_user.email)

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.refresh_tokens(refresh_token)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_refresh_tokens_inactive_user(
    auth_service,
    test_session: AsyncSession,
):
    inactive_user = await UserFactory.create(
        session=test_session,
        email="inactive@example.com",
        password="password123",
        is_active=False,
        is_verified=True,
    )

    refresh_token_str = create_refresh_token(inactive_user.id, inactive_user.email)
    await RefreshTokenFactory.create(
        session=test_session,
        user_id=inactive_user.id,
        token=refresh_token_str,
    )

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.refresh_tokens(refresh_token_str)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "inactive" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_logout_user(
    auth_service,
    test_user,
    test_session: AsyncSession,
):
    refresh_token_str = create_refresh_token(test_user.id, test_user.email)
    refresh_token_obj = await RefreshTokenFactory.create(
        session=test_session,
        user_id=test_user.id,
        token=refresh_token_str,
    )

    await auth_service.logout_user(refresh_token_str)
    await test_session.commit()

    await test_session.refresh(refresh_token_obj)
    assert refresh_token_obj.is_revoked is True
