import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.company.models.types import CompanyRole
from src.backoffice.apps.company.schemas import (
    CompanyMemberCreate,
    CompanyMemberCreateByEmail,
    CompanyMemberUpdateByEmail,
)
from src.backoffice.core.exceptions import NotFoundError
from tests.fixtures.companies import test_company
from tests.fixtures.factories import CompanyMemberFactory, UserFactory


@pytest.mark.asyncio
async def test_add_member_success(
    company_member_service, test_session: AsyncSession, test_company
):
    user = await UserFactory.create(
        session=test_session,
        email="member@example.com",
        password="password",
    )

    member_data = CompanyMemberCreate(user_id=user.id, role=CompanyRole.ADMIN)

    member = await company_member_service.add_member(test_company.id, member_data)

    assert member.id is not None
    assert member.company_id == test_company.id
    assert member.user_id == user.id
    assert member.role == CompanyRole.ADMIN


@pytest.mark.asyncio
async def test_add_member_company_not_found(company_member_service, test_session):
    user = await UserFactory.create(
        session=test_session,
        email="member@example.com",
        password="password",
    )

    member_data = CompanyMemberCreate(user_id=user.id, role=CompanyRole.ADMIN)

    with pytest.raises(NotFoundError) as exc_info:
        await company_member_service.add_member(99999, member_data)

    assert "company" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_add_member_already_exists(
    company_member_service, test_session: AsyncSession, test_company
):
    user = await UserFactory.create(
        session=test_session,
        email="member@example.com",
        password="password",
    )

    await CompanyMemberFactory.create(
        session=test_session,
        company_id=test_company.id,
        user_id=user.id,
        role=CompanyRole.VIEWER,
    )

    member_data = CompanyMemberCreate(user_id=user.id, role=CompanyRole.ADMIN)

    with pytest.raises(ValueError) as exc_info:
        await company_member_service.add_member(test_company.id, member_data)

    assert "already a member" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_add_member_owner_already_exists(
    company_member_service, test_session: AsyncSession, test_company
):
    owner = await UserFactory.create(
        session=test_session,
        email="owner@example.com",
        password="password",
    )
    new_user = await UserFactory.create(
        session=test_session,
        email="newuser@example.com",
        password="password",
    )

    await CompanyMemberFactory.create(
        session=test_session,
        company_id=test_company.id,
        user_id=owner.id,
        role=CompanyRole.OWNER,
    )

    member_data = CompanyMemberCreate(user_id=new_user.id, role=CompanyRole.OWNER)

    with pytest.raises(ValueError) as exc_info:
        await company_member_service.add_member(test_company.id, member_data)

    assert "already has an owner" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_get_user_role_in_company(
    company_member_service, test_session: AsyncSession, test_company
):
    user = await UserFactory.create(
        session=test_session,
        email="member@example.com",
        password="password",
    )

    await CompanyMemberFactory.create(
        session=test_session,
        company_id=test_company.id,
        user_id=user.id,
        role=CompanyRole.ADMIN,
    )

    role = await company_member_service.get_user_role_in_company(
        user.id, test_company.id
    )

    assert role == CompanyRole.ADMIN


@pytest.mark.asyncio
async def test_get_user_role_in_company_not_member(
    company_member_service, test_session: AsyncSession, test_company
):
    user = await UserFactory.create(
        session=test_session,
        email="notmember@example.com",
        password="password",
    )

    role = await company_member_service.get_user_role_in_company(
        user.id, test_company.id
    )

    assert role is None


@pytest.mark.asyncio
async def test_add_member_by_email_success(
    company_member_service, test_session: AsyncSession, test_company
):
    user = await UserFactory.create(
        session=test_session,
        email="newmember@example.com",
        password="password",
    )

    member_data = CompanyMemberCreateByEmail(user_email=user.email)

    member = await company_member_service.add_member_by_email(
        test_company.id, member_data
    )

    assert member.id is not None
    assert member.company_id == test_company.id
    assert member.user_id == user.id
    assert member.role == CompanyRole.VIEWER


@pytest.mark.asyncio
async def test_add_member_by_email_user_not_found(
    company_member_service, test_session: AsyncSession, test_company
):
    member_data = CompanyMemberCreateByEmail(user_email="nonexistent@example.com")

    with pytest.raises(NotFoundError) as exc_info:
        await company_member_service.add_member_by_email(test_company.id, member_data)

    assert "user" in str(exc_info.value).lower()
    assert "email" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_add_member_by_email_already_member(
    company_member_service, test_session: AsyncSession, test_company
):
    user = await UserFactory.create(
        session=test_session,
        email="existing@example.com",
        password="password",
    )

    await CompanyMemberFactory.create(
        session=test_session,
        company_id=test_company.id,
        user_id=user.id,
        role=CompanyRole.VIEWER,
    )

    member_data = CompanyMemberCreateByEmail(user_email=user.email)

    with pytest.raises(ValueError) as exc_info:
        await company_member_service.add_member_by_email(test_company.id, member_data)

    assert "already a member" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_remove_member_by_email_success(
    company_member_service, test_session: AsyncSession, test_company
):
    user = await UserFactory.create(
        session=test_session,
        email="toremove@example.com",
        password="password",
    )

    await CompanyMemberFactory.create(
        session=test_session,
        company_id=test_company.id,
        user_id=user.id,
        role=CompanyRole.VIEWER,
    )

    await company_member_service.remove_member_by_email(test_company.id, user.email)

    role = await company_member_service.get_user_role_in_company(
        user.id, test_company.id
    )
    assert role is None


@pytest.mark.asyncio
async def test_remove_member_by_email_owner(
    company_member_service, test_session: AsyncSession, test_company
):
    user = await UserFactory.create(
        session=test_session,
        email="owner@example.com",
        password="password",
    )

    await CompanyMemberFactory.create(
        session=test_session,
        company_id=test_company.id,
        user_id=user.id,
        role=CompanyRole.OWNER,
    )

    with pytest.raises(ValueError) as exc_info:
        await company_member_service.remove_member_by_email(test_company.id, user.email)

    assert "cannot remove owner" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_remove_member_by_email_user_not_found(
    company_member_service, test_session: AsyncSession, test_company
):
    with pytest.raises(NotFoundError) as exc_info:
        await company_member_service.remove_member_by_email(
            test_company.id, "nonexistent@example.com"
        )

    assert "user" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_remove_member_by_email_not_member(
    company_member_service, test_session: AsyncSession, test_company
):
    user = await UserFactory.create(
        session=test_session,
        email="notmember@example.com",
        password="password",
    )

    with pytest.raises(NotFoundError) as exc_info:
        await company_member_service.remove_member_by_email(test_company.id, user.email)

    assert "not a member" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_update_member_role_by_email_success(
    company_member_service, test_session: AsyncSession, test_company
):
    user = await UserFactory.create(
        session=test_session,
        email="member@example.com",
        password="password",
    )

    await CompanyMemberFactory.create(
        session=test_session,
        company_id=test_company.id,
        user_id=user.id,
        role=CompanyRole.VIEWER,
    )

    member_data = CompanyMemberUpdateByEmail(
        user_email=user.email, role=CompanyRole.ADMIN
    )

    updated_member = await company_member_service.update_member_role_by_email(
        test_company.id, member_data
    )

    assert updated_member.role == CompanyRole.ADMIN
    assert updated_member.user_id == user.id


@pytest.mark.asyncio
async def test_update_member_role_by_email_owner(
    company_member_service, test_session: AsyncSession, test_company
):
    user = await UserFactory.create(
        session=test_session,
        email="owner@example.com",
        password="password",
    )

    await CompanyMemberFactory.create(
        session=test_session,
        company_id=test_company.id,
        user_id=user.id,
        role=CompanyRole.OWNER,
    )

    member_data = CompanyMemberUpdateByEmail(
        user_email=user.email, role=CompanyRole.ADMIN
    )

    with pytest.raises(ValueError) as exc_info:
        await company_member_service.update_member_role_by_email(
            test_company.id, member_data
        )

    assert "cannot change owner role" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_update_member_role_by_email_user_not_found(
    company_member_service, test_session: AsyncSession, test_company
):
    member_data = CompanyMemberUpdateByEmail(
        user_email="nonexistent@example.com", role=CompanyRole.ADMIN
    )

    with pytest.raises(NotFoundError) as exc_info:
        await company_member_service.update_member_role_by_email(
            test_company.id, member_data
        )

    assert "user" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_update_member_role_by_email_not_member(
    company_member_service, test_session: AsyncSession, test_company
):
    user = await UserFactory.create(
        session=test_session,
        email="notmember@example.com",
        password="password",
    )

    member_data = CompanyMemberUpdateByEmail(
        user_email=user.email, role=CompanyRole.ADMIN
    )

    with pytest.raises(NotFoundError) as exc_info:
        await company_member_service.update_member_role_by_email(
            test_company.id, member_data
        )

    assert "not a member" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_get_member_by_email_or_raise_success(
    company_member_service, test_session: AsyncSession, test_company
):
    user = await UserFactory.create(
        session=test_session,
        email="member@example.com",
        password="password",
    )

    await CompanyMemberFactory.create(
        session=test_session,
        company_id=test_company.id,
        user_id=user.id,
        role=CompanyRole.ADMIN,
    )

    member = await company_member_service.get_member_by_email_or_raise(
        test_company.id, user.email
    )

    assert member.user_id == user.id
    assert member.role == CompanyRole.ADMIN


@pytest.mark.asyncio
async def test_get_member_by_email_or_raise_user_not_found(
    company_member_service, test_session: AsyncSession, test_company
):
    with pytest.raises(NotFoundError) as exc_info:
        await company_member_service.get_member_by_email_or_raise(
            test_company.id, "nonexistent@example.com"
        )

    assert "user" in str(exc_info.value).lower()
