from typing import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.account.application import AccountApplication
from src.backoffice.apps.account.services import UserService
from src.backoffice.core.dependencies.service_dependencies import (
    get_account_application,
)
from tests.fixtures.auth import auth_service, inactive_user, test_user  # noqa: F401


@pytest_asyncio.fixture
async def user_service(test_session: AsyncSession) -> UserService:
    return UserService(test_session)


@pytest_asyncio.fixture
async def test_app_with_account(test_session: AsyncSession, test_app) -> AsyncGenerator:
    async def override_get_account_application():
        return AccountApplication(test_session)

    test_app.dependency_overrides[get_account_application] = (
        override_get_account_application
    )

    yield test_app

    if get_account_application in test_app.dependency_overrides:
        del test_app.dependency_overrides[get_account_application]
