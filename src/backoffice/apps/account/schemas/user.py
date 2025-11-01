from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Username can only contain letters, numbers, hyphens and underscores",
    )
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")


class UserCreate(UserBase):
    """Create user schema"""

    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=100,
        description="The password must contain at least 8 characters",
    )
    avatar_url: Optional[str] = Field(None, description="Avatar URL")


class UserCreateInternal(UserBase):
    """Internal user creation schema with password_hash"""

    password_hash: Optional[str] = Field(None, description="Hashed password")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")


class UserUpdate(BaseModel):
    """Update user schema"""

    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Username can only contain letters, numbers, hyphens and underscores",
    )
    first_name: Optional[str] = Field(None, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")


class UserInDB(UserBase):
    """User in the database schema"""

    id: int
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class User(UserInDB):
    """Public user schema"""

    pass


class UserProfile(BaseModel):
    """User profile schema"""

    id: int
    email: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
