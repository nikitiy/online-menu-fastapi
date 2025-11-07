import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.qr_manager.services import QRCodeService
from tests.fixtures.auth import test_user  # noqa: F401
from tests.fixtures.companies import company_with_member, test_company  # noqa: F401


@pytest_asyncio.fixture
async def qr_code_service(test_session: AsyncSession) -> QRCodeService:
    return QRCodeService(test_session)
