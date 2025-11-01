from datetime import datetime, timezone
from typing import Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.account.models import OAuthAccount, User
from src.backoffice.apps.account.repositories import (OAuthAccountRepository,
                                                      UserRepository)


class OAuthAccountService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = OAuthAccountRepository(session)
        self.user_repository = UserRepository(session)

    async def get_or_create_user_by_oauth(
        self, provider: str, provider_user_id: str, user_info: dict
    ) -> Tuple[User, bool]:
        """Get or create user by OAuth provider"""
        # Try to find existing OAuth account
        oauth_account = await self.repository.get_by_provider(
            provider, provider_user_id
        )

        if oauth_account:
            # Update existing user and OAuth account
            user = oauth_account.user
            user.first_name = user_info.get("first_name") or user.first_name
            user.last_name = user_info.get("last_name") or user.last_name
            user.avatar_url = user_info.get("avatar_url") or user.avatar_url
            user.last_login = datetime.now(timezone.utc)

            oauth_account.provider_username = user_info.get("username")
            oauth_account.provider_email = user_info.get("email")
            oauth_account.updated_at = datetime.now(timezone.utc)
            if user_info.get("access_token"):
                oauth_account.access_token = user_info.get("access_token")
            if user_info.get("refresh_token"):
                oauth_account.refresh_token = user_info.get("refresh_token")

            await self.session.flush()
            return user, False

        # Try to find user by email
        email = user_info.get("email")
        if email:
            user = await self.user_repository.get_by_email(email)
            if user:
                # Link OAuth account to existing user
                await self.repository.create(
                    user_id=user.id,
                    provider=provider,
                    provider_user_id=provider_user_id,
                    provider_username=user_info.get("username"),
                    provider_email=email,
                    access_token=user_info.get("access_token"),
                    refresh_token=user_info.get("refresh_token"),
                )
                user.last_login = datetime.now(timezone.utc)
                await self.session.flush()
                return user, False

        # Create new user and OAuth account
        user = await self.user_repository.create(
            email=email or f"{provider_user_id}@{provider}.local",
            username=user_info.get("username"),
            first_name=user_info.get("first_name"),
            last_name=user_info.get("last_name"),
            avatar_url=user_info.get("avatar_url"),
            is_verified=True,
        )

        await self.repository.create(
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            provider_username=user_info.get("username"),
            provider_email=email,
            access_token=user_info.get("access_token"),
            refresh_token=user_info.get("refresh_token"),
        )

        await self.session.flush()
        await self.session.refresh(user)

        return user, True

    async def get_by_provider(
        self, provider: str, provider_user_id: str
    ) -> Optional[OAuthAccount]:
        """Get OAuth account by provider and provider user ID"""
        return await self.repository.get_by_provider(provider, provider_user_id)

    async def create(
        self,
        user_id: int,
        provider: str,
        provider_user_id: str,
        provider_username: Optional[str] = None,
        provider_email: Optional[str] = None,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ) -> OAuthAccount:
        """Create new OAuth account"""
        return await self.repository.create(
            user_id=user_id,
            provider=provider,
            provider_user_id=provider_user_id,
            provider_username=provider_username,
            provider_email=provider_email,
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def update(
        self,
        oauth_account: OAuthAccount,
        provider_username: Optional[str] = None,
        provider_email: Optional[str] = None,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ) -> OAuthAccount:
        """Update OAuth account"""
        if provider_username is not None:
            oauth_account.provider_username = provider_username
        if provider_email is not None:
            oauth_account.provider_email = provider_email
        if access_token is not None:
            oauth_account.access_token = access_token
        if refresh_token is not None:
            oauth_account.refresh_token = refresh_token

        oauth_account.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return oauth_account
