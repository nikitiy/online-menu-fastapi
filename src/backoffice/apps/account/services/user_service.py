from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.account.models import User
from src.backoffice.apps.account.repositories import (OAuthAccountRepository,
                                                      UserRepository)
from src.backoffice.apps.account.schemas import UserCreate, UserCreateInternal
from src.backoffice.apps.account.utils import (get_password_hash,
                                               verify_password)


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = UserRepository(session)
        self.oauth_account_repository = OAuthAccountRepository(session)

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = await self.repository.get_by_email(email)
        if not user or not user.password_hash:
            return None

        if not verify_password(password, str(user.password_hash)):
            return None

        return user

    async def create_user(self, user_data: UserCreate) -> User:
        internal_data = UserCreateInternal(
            email=user_data.email,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            avatar_url=user_data.avatar_url,
            password_hash=(
                get_password_hash(user_data.password) if user_data.password else None
            ),
        )

        return await self.repository.create(
            **internal_data.model_dump(exclude_none=True)
        )

    async def get_by_id(self, user_id: int) -> Optional[User]:
        return await self.repository.get_by_id(user_id)

    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.repository.get_by_email(email)

    async def get_by_username(self, username: str) -> Optional[User]:
        return await self.repository.get_by_username(username)

    async def email_exists(self, email: str) -> bool:
        return await self.repository.email_exists(email)

    async def username_exists(self, username: str) -> bool:
        return await self.repository.username_exists(username)

    async def update_last_login(self, user_id: int):
        """Update user's last login timestamp"""
        user = await self.repository.get_by_id(user_id)
        if user:
            user.last_login = datetime.now(timezone.utc)
            await self.session.flush()
