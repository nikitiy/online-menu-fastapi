from abc import ABC, abstractmethod
from typing import Dict, Optional

import httpx
from authlib.integrations.httpx_client import AsyncOAuth2Client

from src.backoffice.core.config import auth_settings


class OAuthService(ABC):
    def __init__(self):
        self.auth_settings = auth_settings

    @property
    @abstractmethod
    def client_id(self) -> str:
        pass

    @property
    @abstractmethod
    def client_secret(self) -> str:
        pass

    @property
    @abstractmethod
    def redirect_uri(self) -> str:
        pass

    @property
    @abstractmethod
    def token_url(self) -> str:
        pass

    async def _fetch_token_async(self, code: str) -> Optional[Dict]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.token_url,
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": self.redirect_uri,
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                    },
                    headers={"Accept": "application/json"},
                )
                response.raise_for_status()
                return response.json()
            except (httpx.HTTPError, ValueError, KeyError):
                return None

    async def get_user_info(self, access_token: str) -> Optional[Dict]:
        raise NotImplementedError


class GoogleOAuthService(OAuthService):
    def __init__(self):
        super().__init__()
        self._client_id = self.auth_settings.google_client_id
        self._client_secret = self.auth_settings.google_client_secret
        self._redirect_uri = self.auth_settings.google_redirect_uri
        self.scope = "openid email profile"
        self.authorize_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self._token_url = "https://oauth2.googleapis.com/token"
        self.user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"

    @property
    def client_id(self) -> str:
        return self._client_id

    @property
    def client_secret(self) -> str:
        return self._client_secret

    @property
    def redirect_uri(self) -> str:
        return self._redirect_uri

    @property
    def token_url(self) -> str:
        return self._token_url

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        if not self.client_id or not self.client_secret:
            raise ValueError("Google OAuth credentials not configured")

        client = AsyncOAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
        )

        authorization_url, _ = client.create_authorization_url(
            self.authorize_url, state=state
        )
        return authorization_url

    async def get_access_token(self, code: str) -> Optional[Dict]:
        return await self._fetch_token_async(code)

    async def get_user_info(self, access_token: str) -> Optional[Dict]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.user_info_url,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                response.raise_for_status()
                return response.json()
            except (httpx.HTTPError, ValueError, KeyError):
                return None


class YandexOAuthService(OAuthService):
    def __init__(self):
        super().__init__()
        self._client_id = self.auth_settings.yandex_client_id
        self._client_secret = self.auth_settings.yandex_client_secret
        self._redirect_uri = self.auth_settings.yandex_redirect_uri
        self.scope = "login:email login:info"
        self.authorize_url = "https://oauth.yandex.ru/authorize"
        self._token_url = "https://oauth.yandex.ru/token"
        self.user_info_url = "https://login.yandex.ru/info"

    @property
    def client_id(self) -> str:
        return self._client_id

    @property
    def client_secret(self) -> str:
        return self._client_secret

    @property
    def redirect_uri(self) -> str:
        return self._redirect_uri

    @property
    def token_url(self) -> str:
        return self._token_url

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        if not self.client_id or not self.client_secret:
            raise ValueError("Yandex OAuth credentials not configured")

        client = AsyncOAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
        )

        authorization_url, _ = client.create_authorization_url(
            self.authorize_url, state=state
        )
        return authorization_url

    async def get_access_token(self, code: str) -> Optional[Dict]:
        return await self._fetch_token_async(code)

    async def get_user_info(self, access_token: str) -> Optional[Dict]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.user_info_url,
                    headers={"Authorization": f"OAuth {access_token}"},
                )
                response.raise_for_status()
                return response.json()
            except (httpx.HTTPError, ValueError, KeyError):
                return None


class VKOAuthService(OAuthService):
    def __init__(self):
        super().__init__()
        self._client_id = self.auth_settings.vk_client_id
        self._client_secret = self.auth_settings.vk_client_secret
        self._redirect_uri = self.auth_settings.vk_redirect_uri
        self.scope = "email"
        self.authorize_url = "https://oauth.vk.com/authorize"
        self._token_url = "https://oauth.vk.com/access_token"
        self.user_info_url = "https://api.vk.com/method/users.get"

    @property
    def client_id(self) -> str:
        return self._client_id

    @property
    def client_secret(self) -> str:
        return self._client_secret

    @property
    def redirect_uri(self) -> str:
        return self._redirect_uri

    @property
    def token_url(self) -> str:
        return self._token_url

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        if not self.client_id or not self.client_secret:
            raise ValueError("VK OAuth credentials not configured")

        client = AsyncOAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
        )

        authorization_url, _ = client.create_authorization_url(
            self.authorize_url, state=state
        )
        return authorization_url

    async def get_access_token(self, code: str) -> Optional[Dict]:
        return await self._fetch_token_async(code)

    async def get_user_info(self, access_token: str) -> Optional[Dict]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.user_info_url,
                    params={
                        "access_token": access_token,
                        "fields": "id,first_name,last_name,email,photo_200",
                        "v": "5.131",
                    },
                )
                response.raise_for_status()
                data = response.json()
                if "response" in data and data["response"]:
                    user_data = data["response"][0]
                    return {
                        "id": str(user_data.get("id")),
                        "first_name": user_data.get("first_name"),
                        "last_name": user_data.get("last_name"),
                        "email": data.get("email"),
                        "avatar_url": user_data.get("photo_200"),
                    }
                return None
            except (httpx.HTTPError, ValueError, KeyError):
                return None


google_oauth_service = GoogleOAuthService()
yandex_oauth_service = YandexOAuthService()
vk_oauth_service = VKOAuthService()
