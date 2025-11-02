import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.account.schemas import UserCreate
from src.backoffice.apps.account.utils import verify_password
from tests.fixtures.factories import UserFactory


@pytest.mark.asyncio
async def test_authenticate_user_success(user_service, test_user):
    user = await user_service.authenticate_user(test_user.email, "test_password_123")

    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email


@pytest.mark.asyncio
async def test_authenticate_user_invalid_password(user_service, test_user):
    user = await user_service.authenticate_user(test_user.email, "wrong_password")

    assert user is None


@pytest.mark.asyncio
async def test_authenticate_user_not_found(user_service):
    user = await user_service.authenticate_user(
        "nonexistent@example.com", "password123"
    )

    assert user is None


@pytest.mark.asyncio
async def test_authenticate_user_no_password_hash(
    user_service, test_session: AsyncSession
):
    oauth_user = await UserFactory.create(
        session=test_session,
        email="oauth@example.com",
        password=None,
        is_active=True,
        is_verified=True,
    )

    user = await user_service.authenticate_user(oauth_user.email, "password123")

    assert user is None


@pytest.mark.asyncio
async def test_create_user_success(user_service):
    user_data = UserCreate(
        email="newuser@example.com",
        password="password123",
        username="newuser",
        first_name="New",
        last_name="User",
    )

    user = await user_service.create_user(user_data)

    assert user.id is not None
    assert user.email == "newuser@example.com"
    assert user.username == "newuser"
    assert user.first_name == "New"
    assert user.last_name == "User"
    assert user.password_hash is not None
    assert verify_password("password123", user.password_hash)


@pytest.mark.asyncio
async def test_create_user_without_password(user_service):
    user_data = UserCreate(
        email="oauthuser@example.com",
        password=None,
        username="oauthuser",
    )

    user = await user_service.create_user(user_data)

    assert user.id is not None
    assert user.email == "oauthuser@example.com"
    assert user.username == "oauthuser"
    assert user.password_hash is None


@pytest.mark.asyncio
async def test_get_by_id_success(user_service, test_user):
    user = await user_service.get_by_id(test_user.id)

    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email


@pytest.mark.asyncio
async def test_get_by_id_not_found(user_service):
    user = await user_service.get_by_id(99999)

    assert user is None


@pytest.mark.asyncio
async def test_get_by_email_success(user_service, test_user):
    user = await user_service.get_by_email(test_user.email)

    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email


@pytest.mark.asyncio
async def test_get_by_email_not_found(user_service):
    user = await user_service.get_by_email("nonexistent@example.com")

    assert user is None


@pytest.mark.asyncio
async def test_get_by_username_success(user_service, test_session: AsyncSession):
    await UserFactory.create(
        session=test_session,
        email="username@example.com",
        username="testusername",
        password="password123",
    )

    user = await user_service.get_by_username("testusername")

    assert user is not None
    assert user.username == "testusername"
    assert user.email == "username@example.com"


@pytest.mark.asyncio
async def test_get_by_username_not_found(user_service):
    user = await user_service.get_by_username("nonexistent_username")

    assert user is None


@pytest.mark.asyncio
async def test_email_exists_true(user_service, test_user):
    exists = await user_service.email_exists(test_user.email)

    assert exists is True


@pytest.mark.asyncio
async def test_email_exists_false(user_service):
    exists = await user_service.email_exists("nonexistent@example.com")

    assert exists is False


@pytest.mark.asyncio
async def test_username_exists_true(user_service, test_session: AsyncSession):
    await UserFactory.create(
        session=test_session,
        email="user@example.com",
        username="existingusername",
        password="password123",
    )

    exists = await user_service.username_exists("existingusername")

    assert exists is True


@pytest.mark.asyncio
async def test_username_exists_false(user_service):
    exists = await user_service.username_exists("nonexistent_username")

    assert exists is False


@pytest.mark.asyncio
async def test_update_last_login(user_service, test_user, test_session: AsyncSession):
    assert test_user.last_login is None

    await user_service.update_last_login(test_user.id)
    await test_session.refresh(test_user)

    assert test_user.last_login is not None
