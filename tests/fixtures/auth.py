import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.account.services import AuthService
from tests.fixtures.factories import RefreshTokenFactory, UserFactory
from tests.utils.auth import create_refresh_token


@pytest_asyncio.fixture
async def auth_service(test_session: AsyncSession) -> AuthService:
    return await AuthService.create(test_session)


@pytest_asyncio.fixture
async def test_user(test_session: AsyncSession):
    user = await UserFactory.create(
        session=test_session,
        email="test@example.com",
        password="test_password_123",
        is_active=True,
        is_verified=True,
    )
    return user


@pytest_asyncio.fixture
async def inactive_user(test_session: AsyncSession):
    user = await UserFactory.create(
        session=test_session,
        email="inactive@example.com",
        password="password123",
        is_active=False,
        is_verified=True,
    )
    return user


@pytest_asyncio.fixture
async def test_refresh_token(test_user, test_session: AsyncSession):
    token = create_refresh_token(test_user.id, test_user.email)
    refresh_token_obj = await RefreshTokenFactory.create(
        session=test_session,
        user_id=test_user.id,
        token=token,
    )
    return refresh_token_obj.token
