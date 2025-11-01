from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.backoffice.apps.account.models import OAuthAccount, User
from src.backoffice.core.repositories import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_email_with_oauth(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(User)
            .where(User.email == email)
            .options(selectinload(User.oauth_accounts))
        )
        return result.scalar_one_or_none()

    async def get_by_oauth_provider(
        self, provider: str, provider_user_id: str
    ) -> Optional[User]:
        result = await self.session.execute(
            select(User)
            .join(OAuthAccount, User.id == OAuthAccount.user_id)
            .where(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_user_id == provider_user_id,
            )
            .options(selectinload(User.oauth_accounts))
        )
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        result = await self.session.execute(select(User.id).where(User.email == email))
        return result.scalar_one_or_none() is not None

    async def username_exists(self, username: str) -> bool:
        result = await self.session.execute(
            select(User.id).where(User.username == username)
        )
        return result.scalar_one_or_none() is not None
