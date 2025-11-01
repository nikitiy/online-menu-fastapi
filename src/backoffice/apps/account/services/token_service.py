from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.account.models import RefreshToken
from src.backoffice.apps.account.repositories import RefreshTokenRepository


class TokenService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = RefreshTokenRepository(session)

    async def create_refresh_token(
        self, user_id: int, token: str, expires_at: datetime
    ) -> RefreshToken:
        return await self.repository.create(
            user_id=user_id, token=token, expires_at=expires_at
        )

    async def get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        return await self.repository.get_by_token(token)

    async def revoke_refresh_token(self, token: str) -> bool:
        refresh_token = await self.repository.get_by_token(token)
        if refresh_token:
            refresh_token.is_revoked = True
            await self.session.flush()
            return True
        return False

    async def revoke_all_user_tokens(self, user_id: int) -> int:
        tokens = await self.repository.get_active_tokens_by_user_id(user_id)

        for token in tokens:
            token.is_revoked = True

        await self.session.flush()
        return len(tokens)

    async def cleanup_expired_tokens(self) -> int:
        expired_tokens = await self.repository.get_expired_tokens()

        count = 0
        for token in expired_tokens:
            await self.repository.delete(token.id)
            count += 1

        return count

    async def get_user_tokens(self, user_id: int) -> List[RefreshToken]:
        return await self.repository.get_active_tokens_by_user_id(user_id)
