from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.backoffice.apps.account.models import OAuthAccount
from src.backoffice.core.repositories import BaseRepository


class OAuthAccountRepository(BaseRepository[OAuthAccount]):
    def __init__(self, session: AsyncSession):
        super().__init__(OAuthAccount, session)

    async def get_by_provider(
        self, provider: str, provider_user_id: str
    ) -> Optional[OAuthAccount]:
        result = await self.session.execute(
            select(OAuthAccount)
            .where(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_user_id == provider_user_id,
            )
            .options(selectinload(OAuthAccount.user))
        )
        return result.scalar_one_or_none()

    async def get_by_user_id_and_provider(
        self, user_id: int, provider: str
    ) -> Optional[OAuthAccount]:
        result = await self.session.execute(
            select(OAuthAccount).where(
                OAuthAccount.user_id == user_id,
                OAuthAccount.provider == provider,
            )
        )
        return result.scalar_one_or_none()
