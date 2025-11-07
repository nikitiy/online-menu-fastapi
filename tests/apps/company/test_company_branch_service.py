import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.company.schemas import CompanyBranchCreate, CompanyBranchUpdate
from src.backoffice.core.exceptions import NotFoundError
from tests.fixtures.companies import test_company
from tests.fixtures.factories import CompanyFactory


@pytest.mark.asyncio
async def test_create_branch_success(
    company_branch_service, test_session: AsyncSession, test_company
):
    branch_data = CompanyBranchCreate(
        company_id=test_company.id,
        name="Main Branch",
        description="Main branch description",
        latitude=55.7558,
        longitude=37.6173,
        phone="+7-999-123-45-67",
        email="branch@example.com",
    )

    branch = await company_branch_service.create_branch(branch_data)

    assert branch.id is not None
    assert branch.company_id == test_company.id
    assert branch.name == "Main Branch"
    assert branch.description == "Main branch description"
    assert branch.latitude == 55.7558
    assert branch.longitude == 37.6173
    assert branch.phone == "+7-999-123-45-67"
    assert branch.email == "branch@example.com"
    assert branch.is_active is True
    assert branch.is_verified is False


@pytest.mark.asyncio
async def test_get_branch_by_id_success(
    company_branch_service, test_session: AsyncSession, test_company
):
    branch_data = CompanyBranchCreate(
        company_id=test_company.id,
        name="Test Branch",
    )
    created_branch = await company_branch_service.create_branch(branch_data)

    branch = await company_branch_service.get_branch_by_id_or_raise(created_branch.id)

    assert branch.id == created_branch.id
    assert branch.name == "Test Branch"
    assert branch.company_id == test_company.id


@pytest.mark.asyncio
async def test_get_branch_by_id_not_found(company_branch_service):
    with pytest.raises(NotFoundError) as exc_info:
        await company_branch_service.get_branch_by_id_or_raise(99999)

    assert "not found" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_get_branches_by_company(
    company_branch_service, test_session: AsyncSession
):
    company1 = await CompanyFactory.create(
        session=test_session,
        name="Company 1",
        subdomain="company1",
    )
    company2 = await CompanyFactory.create(
        session=test_session,
        name="Company 2",
        subdomain="company2",
    )

    branch1_data = CompanyBranchCreate(company_id=company1.id, name="Branch 1")
    branch2_data = CompanyBranchCreate(company_id=company1.id, name="Branch 2")
    branch3_data = CompanyBranchCreate(company_id=company2.id, name="Branch 3")

    await company_branch_service.create_branch(branch1_data)
    await company_branch_service.create_branch(branch2_data)
    await company_branch_service.create_branch(branch3_data)

    branches = await company_branch_service.get_branches_by_company(company1.id)

    assert len(branches) == 2
    branch_names = {b.name for b in branches}
    assert "Branch 1" in branch_names
    assert "Branch 2" in branch_names
    assert "Branch 3" not in branch_names


@pytest.mark.asyncio
async def test_get_branches_by_company_empty(
    company_branch_service, test_session: AsyncSession, test_company
):
    branches = await company_branch_service.get_branches_by_company(test_company.id)

    assert len(branches) == 0


@pytest.mark.asyncio
async def test_update_branch_success(
    company_branch_service, test_session: AsyncSession, test_company
):
    branch_data = CompanyBranchCreate(
        company_id=test_company.id,
        name="Original Name",
        description="Original description",
    )
    created_branch = await company_branch_service.create_branch(branch_data)

    update_data = CompanyBranchUpdate(
        name="Updated Name",
        description="Updated description",
        is_active=False,
        is_verified=True,
    )

    updated_branch = await company_branch_service.update_branch_or_raise(
        created_branch.id, update_data
    )

    assert updated_branch.id == created_branch.id
    assert updated_branch.name == "Updated Name"
    assert updated_branch.description == "Updated description"
    assert updated_branch.is_active is False
    assert updated_branch.is_verified is True


@pytest.mark.asyncio
async def test_update_branch_partial(
    company_branch_service, test_session: AsyncSession, test_company
):
    branch_data = CompanyBranchCreate(
        company_id=test_company.id,
        name="Original Name",
        description="Original description",
        phone="+7-999-111-11-11",
    )
    created_branch = await company_branch_service.create_branch(branch_data)

    update_data = CompanyBranchUpdate(name="Updated Name")

    updated_branch = await company_branch_service.update_branch_or_raise(
        created_branch.id, update_data
    )

    assert updated_branch.name == "Updated Name"
    assert updated_branch.description == "Original description"
    assert updated_branch.phone == "+7-999-111-11-11"


@pytest.mark.asyncio
async def test_update_branch_not_found(company_branch_service):
    update_data = CompanyBranchUpdate(name="Updated Name")

    with pytest.raises(NotFoundError) as exc_info:
        await company_branch_service.update_branch_or_raise(99999, update_data)

    assert "not found" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_delete_branch_success(
    company_branch_service, test_session: AsyncSession, test_company
):
    branch_data = CompanyBranchCreate(
        company_id=test_company.id,
        name="Branch to Delete",
    )
    created_branch = await company_branch_service.create_branch(branch_data)

    await company_branch_service.delete_branch_or_raise(created_branch.id)

    with pytest.raises(NotFoundError):
        await company_branch_service.get_branch_by_id_or_raise(created_branch.id)


@pytest.mark.asyncio
async def test_delete_branch_not_found(company_branch_service):
    with pytest.raises(NotFoundError) as exc_info:
        await company_branch_service.delete_branch_or_raise(99999)

    assert "not found" in str(exc_info.value).lower()
