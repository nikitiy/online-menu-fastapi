from fastapi import APIRouter

from src.backoffice.apps.account.schemas import (
    LoginRequest,
    OAuthProvider,
    OAuthProviders,
    RefreshTokenRequest,
    RegisterRequest,
    Token,
    UserProfile,
)
from src.backoffice.core.config import auth_settings
from src.backoffice.core.dependencies import AccountApplicationDep, AuthenticatedUserDep

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=UserProfile)
async def get_request_user_profile(
    request_user: AuthenticatedUserDep,
):
    """Get the request user's profile"""
    return request_user


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest, account_app: AccountApplicationDep
):
    """Refresh access token"""
    return await account_app.refresh_tokens(refresh_data.refresh_token)


@router.post("/logout")
async def logout(refresh_data: RefreshTokenRequest, account_app: AccountApplicationDep):
    """Log out"""
    await account_app.logout_user(refresh_data.refresh_token)
    return {"message": "Successfully logged out"}


@router.post("/register", response_model=Token)
async def register(register_data: RegisterRequest, account_app: AccountApplicationDep):
    """User registration by email"""
    tokens, _ = await account_app.register_user(register_data)
    return tokens


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, account_app: AccountApplicationDep):
    """User login using email and password"""
    tokens, _ = await account_app.authenticate_user(login_data)
    return tokens


@router.get("/providers", response_model=OAuthProviders)
async def get_oauth_providers():
    """Get a list of available OAuth providers"""
    providers = []

    # Google
    if auth_settings.google_client_id:
        providers.append(
            OAuthProvider(
                name="google",
                display_name="Google",
                auth_url=f"{auth_settings.backend_url}/api/v1/auth/google",
                enabled=True,
            )
        )

    # Yandex
    if auth_settings.yandex_client_id:
        providers.append(
            OAuthProvider(
                name="yandex",
                display_name="Yandex",
                auth_url=f"{auth_settings.backend_url}/api/v1/auth/yandex",
                enabled=True,
            )
        )

    # VK
    if auth_settings.vk_client_id:
        providers.append(
            OAuthProvider(
                name="vk",
                display_name="VKontakte",
                auth_url=f"{auth_settings.backend_url}/api/v1/auth/vk",
                enabled=True,
            )
        )

    return OAuthProviders(providers=providers)


@router.get("/google")
async def google_auth(account_app: AccountApplicationDep):
    """Start authorization via Google"""
    return await account_app.get_google_auth_url()


@router.get("/google/callback")
async def google_callback(code: str, account_app: AccountApplicationDep):
    """Callback for Google OAuth"""
    # TODO: Implement state validation for CSRF protection
    # For now, we accept any state or no state
    # In production, you should validate the state parameter
    return await account_app.handle_google_callback(code)


@router.get("/yandex")
async def yandex_auth(account_app: AccountApplicationDep):
    """Start authorization via Yandex"""
    return await account_app.get_yandex_auth_url()


@router.get("/yandex/callback")
async def yandex_callback(code: str, account_app: AccountApplicationDep):
    """Callback for Yandex OAuth"""
    # TODO: Implement state validation for CSRF protection
    # For now, we accept any state or no state
    # In production, you should validate the state parameter
    return await account_app.handle_yandex_callback(code)


@router.get("/vk")
async def vk_auth(account_app: AccountApplicationDep):
    """Start authorization via VK"""
    return await account_app.get_vk_auth_url()


@router.get("/vk/callback")
async def vk_callback(code: str, account_app: AccountApplicationDep):
    """Callback for VK OAuth"""
    # TODO: Implement state validation for CSRF protection
    # For now, we accept any state or no state
    # In production, you should validate the state parameter
    return await account_app.handle_vk_callback(code)
