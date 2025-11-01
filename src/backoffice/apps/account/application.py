from typing import Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.account.models import User
from src.backoffice.apps.account.schemas import LoginRequest, RegisterRequest, Token
from src.backoffice.apps.account.services import (
    AuthService,
    GoogleOAuthService,
    VKOAuthService,
    YandexOAuthService,
)


class AccountApplication:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.auth_service = None

    async def _get_auth_service(self) -> AuthService:
        if self.auth_service is None:
            self.auth_service = await AuthService.create(self.session)
        return self.auth_service

    async def register_user(self, register_data: RegisterRequest) -> Tuple[Token, User]:
        auth_service = await self._get_auth_service()
        tokens, user = await auth_service.register_user(register_data)
        await self.session.commit()
        return tokens, user

    async def authenticate_user(self, login_data: LoginRequest) -> Tuple[Token, User]:
        auth_service = await self._get_auth_service()
        tokens, user = await auth_service.authenticate_user(login_data)
        await self.session.commit()
        return tokens, user

    async def refresh_tokens(self, refresh_token: str) -> Token:
        auth_service = await self._get_auth_service()
        tokens = await auth_service.refresh_tokens(refresh_token)
        await self.session.commit()
        return tokens

    async def logout_user(self, refresh_token: str):
        auth_service = await self._get_auth_service()
        await auth_service.logout_user(refresh_token)
        await self.session.commit()

    async def create_tokens_for_user(self, user: User) -> Token:
        auth_service = await self._get_auth_service()
        tokens = await auth_service.create_tokens_for_user(user)
        await self.session.commit()
        return tokens

    @staticmethod
    async def get_google_auth_url() -> dict:
        google_oauth_service = GoogleOAuthService()
        return AuthService.get_google_auth_url(google_oauth_service)

    async def handle_google_callback(self, code: str) -> dict:
        auth_service = await self._get_auth_service()
        google_oauth_service = GoogleOAuthService()
        result = await auth_service.handle_google_callback(code, google_oauth_service)
        await self.session.commit()
        return result

    @staticmethod
    async def get_yandex_auth_url() -> dict:
        yandex_oauth_service = YandexOAuthService()
        return AuthService.get_yandex_auth_url(yandex_oauth_service)

    async def handle_yandex_callback(self, code: str) -> dict:
        auth_service = await self._get_auth_service()
        yandex_oauth_service = YandexOAuthService()
        result = await auth_service.handle_yandex_callback(code, yandex_oauth_service)
        await self.session.commit()
        return result

    @staticmethod
    async def get_vk_auth_url() -> dict:
        vk_oauth_service = VKOAuthService()
        return AuthService.get_vk_auth_url(vk_oauth_service)

    async def handle_vk_callback(self, code: str) -> dict:
        auth_service = await self._get_auth_service()
        vk_oauth_service = VKOAuthService()
        result = await auth_service.handle_vk_callback(code, vk_oauth_service)
        await self.session.commit()
        return result
