from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.qr_manager.models import QRCode
from src.backoffice.core.repositories import BaseRepository


class QRCodeRepository(BaseRepository[QRCode]):
    def __init__(self, session: AsyncSession):
        super().__init__(QRCode, session)

    async def get_by_url_hash(self, url_hash: str) -> Optional[QRCode]:
        result = await self.session.execute(
            select(QRCode).where(QRCode.url_hash == url_hash)
        )
        return result.scalar_one_or_none()

    async def get_by_company_branch_id(
        self, company_branch_id: int
    ) -> Optional[QRCode]:
        result = await self.session.execute(
            select(QRCode).where(QRCode.company_branch_id == company_branch_id)
        )
        return result.scalar_one_or_none()
