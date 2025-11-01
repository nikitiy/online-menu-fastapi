from datetime import datetime, timedelta, timezone
from typing import Tuple

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.account.models import User
from src.backoffice.apps.account.schemas import (LoginRequest, RegisterRequest,
                                                 Token, UserCreate, UserLogin)
from src.backoffice.apps.account.services.jwt_service import jwt_service
from src.backoffice.apps.account.services.oauth_account_service import \
    OAuthAccountService
from src.backoffice.apps.account.services.token_service import TokenService
from src.backoffice.apps.account.services.user_service import UserService
from src.backoffice.core.config import auth_settings
from src.backoffice.core.dependencies import SessionDep


class AuthService:
    def __init__(
        self,
        user_service: UserService,
        token_service: TokenService,
        oauth_account_service: OAuthAccountService,
    ):
        self.user_service = user_service
        self.token_service = token_service
        self.oauth_account_service = oauth_account_service

    @classmethod
    async def create(cls, session: AsyncSession) -> "AuthService":
        user_service = UserService(session)
        token_service = TokenService(session)
        oauth_account_service = OAuthAccountService(session)
        return cls(user_service, token_service, oauth_account_service)

    async def create_tokens_for_user(self, user: User) -> Token:
        token_data = {"user_id": user.id, "email": user.email}
        access_token = jwt_service.create_access_token(token_data)
        new_refresh_token = jwt_service.create_refresh_token(token_data)

        expires_at = datetime.now(timezone.utc) + timedelta(
            days=auth_settings.refresh_token_expire_days
        )
        await self.token_service.create_refresh_token(
            user.id, new_refresh_token, expires_at
        )

        return Token(access_token=access_token, refresh_token=new_refresh_token)

    async def register_user(self, register_data: RegisterRequest) -> Tuple[Token, User]:
        if await self.user_service.email_exists(str(register_data.email)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        if register_data.username:
            if await self.user_service.username_exists(register_data.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this username already exists",
                )

        user_data = UserCreate(
            email=register_data.email,
            username=register_data.username,
            first_name=register_data.first_name,
            last_name=register_data.last_name,
            password=register_data.password,
            avatar_url=None,
        )

        user = await self.user_service.create_user(user_data)
        tokens = await self.create_tokens_for_user(user)

        return tokens, user

    async def authenticate_user(self, login_data: LoginRequest) -> Tuple[Token, User]:
        user = await self.user_service.authenticate_user(
            str(login_data.email), login_data.password
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="The user account is inactive",
            )

        await self.user_service.update_last_login(user.id)

        tokens = await self.create_tokens_for_user(user)
        return tokens, user

    async def refresh_tokens(self, refresh_token: str) -> Token:
        payload = jwt_service.verify_refresh_token(refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        refresh_token_obj = await self.token_service.get_refresh_token(refresh_token)
        if not refresh_token_obj:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        user = await self.user_service.get_by_id(refresh_token_obj.user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        await self.token_service.revoke_refresh_token(refresh_token)

        return await self.create_tokens_for_user(user)

    async def logout_user(self, refresh_token: str):
        await self.token_service.revoke_refresh_token(refresh_token)

    async def handle_oauth_callback(
        self, provider: str, code: str, oauth_service
    ) -> Tuple[Token, UserLogin, bool]:
        token_data = await oauth_service.get_access_token(code)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get access token from {provider.title()}",
            )

        user_info = await oauth_service.get_user_info(token_data["access_token"])
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get user info from {provider.title()}",
            )

        user, is_new = await self.oauth_account_service.get_or_create_user_by_oauth(
            provider=provider,
            provider_user_id=user_info["id"],
            user_info={
                **user_info,
                "access_token": token_data["access_token"],
                "refresh_token": token_data.get("refresh_token"),
            },
        )

        tokens = await self.create_tokens_for_user(user)
        user_login = UserLogin.model_validate(user)

        return tokens, user_login, is_new

    @staticmethod
    def get_google_auth_url(google_oauth_service) -> dict:
        auth_url = google_oauth_service.get_authorization_url()
        return {"auth_url": auth_url}

    @staticmethod
    def get_yandex_auth_url(yandex_oauth_service) -> dict:
        auth_url = yandex_oauth_service.get_authorization_url()
        return {"auth_url": auth_url}

    @staticmethod
    def get_vk_auth_url(vk_oauth_service) -> dict:
        auth_url = vk_oauth_service.get_authorization_url()
        return {"auth_url": auth_url}

    async def handle_google_callback(self, code: str, google_oauth_service) -> dict:
        tokens, user_login, is_new = await self.handle_oauth_callback(
            "google", code, google_oauth_service
        )
        return {
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "token_type": "bearer",
            "user": user_login,
            "is_new_user": is_new,
        }

    async def handle_yandex_callback(self, code: str, yandex_oauth_service) -> dict:
        tokens, user_login, is_new = await self.handle_oauth_callback(
            "yandex", code, yandex_oauth_service
        )
        return {
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "token_type": "bearer",
            "user": user_login,
            "is_new_user": is_new,
        }

    async def handle_vk_callback(self, code: str, vk_oauth_service) -> dict:
        tokens, user_login, is_new = await self.handle_oauth_callback(
            "vk", code, vk_oauth_service
        )
        return {
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "token_type": "bearer",
            "user": user_login,
            "is_new_user": is_new,
        }


async def get_auth_service(session: SessionDep) -> AuthService:
    return await AuthService.create(session)
