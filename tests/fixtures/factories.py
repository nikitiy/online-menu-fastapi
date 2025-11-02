from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.account.models import RefreshToken, User
from src.backoffice.apps.account.utils import get_password_hash
from src.backoffice.apps.company.models import Company, CompanyMember
from src.backoffice.apps.company.models.types import (
    CompanyEstablishmentType,
    CompanyRole,
    CuisineCategory,
)


class UserFactory:
    @staticmethod
    async def create(
        session: AsyncSession,
        email: str = "test@example.com",
        password: Optional[str] = "test_password_123",
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        is_active: bool = True,
        is_verified: bool = True,
        commit: bool = True,
    ) -> User:
        password_hash = get_password_hash(password) if password else None
        user = User(
            email=email,
            password_hash=password_hash,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
            is_verified=is_verified,
        )
        session.add(user)
        if commit:
            await session.commit()
            await session.refresh(user)
        return user


class RefreshTokenFactory:
    @staticmethod
    async def create(
        session: AsyncSession,
        user_id: int,
        token: str,
        expires_at: Optional[datetime] = None,
        is_revoked: bool = False,
        commit: bool = True,
    ) -> RefreshToken:
        if expires_at is None:
            expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            is_revoked=is_revoked,
        )
        session.add(refresh_token)
        if commit:
            await session.commit()
            await session.refresh(refresh_token)
        return refresh_token


class CompanyFactory:
    @staticmethod
    async def create(
        session: AsyncSession,
        name: str = "Test Restaurant",
        description: Optional[str] = "A test restaurant",
        subdomain: str = "test-restaurant",
        type_of_establishment: CompanyEstablishmentType = CompanyEstablishmentType.RESTAURANT,
        cuisine_category: CuisineCategory = CuisineCategory.JAPANESE,
        commit: bool = True,
    ) -> Company:
        company = Company(
            name=name,
            description=description,
            subdomain=subdomain,
            type_of_establishment=type_of_establishment,
            cuisine_category=cuisine_category,
        )
        session.add(company)
        if commit:
            await session.commit()
            await session.refresh(company)
        return company


class CompanyMemberFactory:
    @staticmethod
    async def create(
        session: AsyncSession,
        company_id: int,
        user_id: int,
        role: CompanyRole = CompanyRole.OWNER,
        commit: bool = True,
    ) -> CompanyMember:
        member = CompanyMember(
            company_id=company_id,
            user_id=user_id,
            role=role,
        )
        session.add(member)
        if commit:
            await session.commit()
            await session.refresh(member)
        return member
