from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.account.models import RefreshToken
from src.backoffice.core.repositories import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session: AsyncSession):
        super().__init__(RefreshToken, session)

    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.token == token,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.now(timezone.utc),
            )
        )
        return result.scalar_one_or_none()

    async def get_active_tokens_by_user_id(self, user_id: int) -> List[RefreshToken]:
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.now(timezone.utc),
            )
        )
        return list(result.scalars().all())

    async def get_expired_tokens(self) -> List[RefreshToken]:
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.expires_at < datetime.now(timezone.utc)
            )
        )
        return list(result.scalars().all())
