from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """Token schema"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenCreate(BaseModel):
    """Refresh token creation schema"""

    user_id: int
    token: str
    expires_at: datetime


class LoginRequest(BaseModel):
    """Login request schema"""

    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Registration request schema"""

    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="The password must contain at least 8 characters",
    )
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Username can only contain letters, numbers, hyphens and underscores",
    )
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""

    refresh_token: str


class OAuthCallback(BaseModel):
    """OAuth callback schema"""

    code: str
    state: Optional[str] = None


class OAuthProvider(BaseModel):
    """OAuth provider schema"""

    name: str
    display_name: str
    auth_url: str
    enabled: bool


class OAuthProviders(BaseModel):
    """OAuth providers schema"""

    providers: list[OAuthProvider]


class UserLogin(BaseModel):
    """User login schema"""

    user_id: int
    email: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    is_superuser: bool
