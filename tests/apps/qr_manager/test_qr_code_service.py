import hashlib

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.qr_manager.schemas import QRCodeCreate, QRCodeUpdate
from src.backoffice.apps.qr_manager.services import QRCodeService
from src.backoffice.core.exceptions import NotFoundError
from tests.fixtures.companies import test_company
from tests.fixtures.factories import CompanyBranchFactory, QRCodeFactory


@pytest.mark.asyncio
async def test_create_qr_code_success(
    qr_code_service, test_session: AsyncSession, test_company
):
    branch = await CompanyBranchFactory.create(
        session=test_session,
        company_id=test_company.id,
        name="Test Branch",
    )

    url_hash = hashlib.sha256(f"http://test/branch/{branch.id}".encode()).hexdigest()
    qr_code_data = QRCodeCreate(
        company_branch_id=branch.id,
        url_hash=url_hash,
        qr_options={"version": 1, "box_size": 10},
    )

    qr_code = await qr_code_service.create_qr_code(qr_code_data)

    assert qr_code.id is not None
    assert qr_code.company_branch_id == branch.id
    assert qr_code.url_hash == url_hash
    assert qr_code.qr_options == {"version": 1, "box_size": 10}
    assert qr_code.scan_count == 0
    assert qr_code.last_scanned is None


@pytest.mark.asyncio
async def test_create_qr_code_without_options(
    qr_code_service, test_session: AsyncSession, test_company
):
    branch = await CompanyBranchFactory.create(
        session=test_session,
        company_id=test_company.id,
        name="Test Branch",
    )

    url_hash = hashlib.sha256(f"http://test/branch/{branch.id}".encode()).hexdigest()
    qr_code_data = QRCodeCreate(
        company_branch_id=branch.id,
        url_hash=url_hash,
    )

    qr_code = await qr_code_service.create_qr_code(qr_code_data)

    assert qr_code.id is not None
    assert qr_code.qr_options == {}


@pytest.mark.asyncio
async def test_create_qr_code_duplicate_branch(
    qr_code_service, test_session: AsyncSession, test_company
):
    branch = await CompanyBranchFactory.create(
        session=test_session,
        company_id=test_company.id,
        name="Test Branch",
    )

    url_hash = hashlib.sha256(f"http://test/branch/{branch.id}".encode()).hexdigest()
    qr_code_data = QRCodeCreate(
        company_branch_id=branch.id,
        url_hash=url_hash,
    )

    await qr_code_service.create_qr_code(qr_code_data)

    with pytest.raises(ValueError) as exc_info:
        await qr_code_service.create_qr_code(qr_code_data)

    assert "already exists" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_create_qr_code_nonexistent_branch(qr_code_service):
    url_hash = hashlib.sha256("http://test/branch/99999".encode()).hexdigest()
    qr_code_data = QRCodeCreate(
        company_branch_id=99999,
        url_hash=url_hash,
    )

    with pytest.raises(NotFoundError) as exc_info:
        await qr_code_service.create_qr_code(qr_code_data)

    assert "not found" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_get_qr_code_by_company_branch_success(
    qr_code_service, test_session: AsyncSession, test_company
):
    branch = await CompanyBranchFactory.create(
        session=test_session,
        company_id=test_company.id,
        name="Test Branch",
    )

    qr_code = await QRCodeFactory.create(
        session=test_session,
        company_branch_id=branch.id,
    )

    result = await qr_code_service.get_qr_code_by_company_branch(branch.id)

    assert result.id == qr_code.id
    assert result.company_branch_id == branch.id


@pytest.mark.asyncio
async def test_get_qr_code_by_company_branch_not_found(
    qr_code_service, test_session: AsyncSession, test_company
):
    branch = await CompanyBranchFactory.create(
        session=test_session,
        company_id=test_company.id,
        name="Test Branch",
    )

    with pytest.raises(NotFoundError) as exc_info:
        await qr_code_service.get_qr_code_by_company_branch(branch.id)

    assert "not found" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_get_company_branch_by_qr_code_hash_success(
    qr_code_service, test_session: AsyncSession, test_company
):
    branch = await CompanyBranchFactory.create(
        session=test_session,
        company_id=test_company.id,
        name="Test Branch",
    )

    url_hash = hashlib.sha256(f"http://test/branch/{branch.id}".encode()).hexdigest()
    await QRCodeFactory.create(
        session=test_session,
        company_branch_id=branch.id,
        url_hash=url_hash,
    )

    result = await qr_code_service.get_company_branch_by_qr_code_hash(url_hash)

    assert result.id == branch.id
    assert result.company_id == test_company.id


@pytest.mark.asyncio
async def test_get_company_branch_by_qr_code_hash_not_found(qr_code_service):
    url_hash = hashlib.sha256("http://test/branch/99999".encode()).hexdigest()

    with pytest.raises(NotFoundError) as exc_info:
        await qr_code_service.get_company_branch_by_qr_code_hash(url_hash)

    assert "not found" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_update_qr_code_by_hash_success(
    qr_code_service, test_session: AsyncSession, test_company
):
    branch = await CompanyBranchFactory.create(
        session=test_session,
        company_id=test_company.id,
        name="Test Branch",
    )

    url_hash = hashlib.sha256(f"http://test/branch/{branch.id}".encode()).hexdigest()
    qr_code = await QRCodeFactory.create(
        session=test_session,
        company_branch_id=branch.id,
        url_hash=url_hash,
        qr_options={"version": 1},
    )

    update_data = QRCodeUpdate(
        qr_options={"version": 2, "box_size": 15, "fill_color": "blue"}
    )

    updated_qr_code = await qr_code_service.update_qr_code_by_hash(
        url_hash, update_data
    )

    assert updated_qr_code.id == qr_code.id
    assert updated_qr_code.qr_options == {
        "version": 2,
        "box_size": 15,
        "fill_color": "blue",
    }


@pytest.mark.asyncio
async def test_update_qr_code_by_hash_partial(
    qr_code_service, test_session: AsyncSession, test_company
):
    branch = await CompanyBranchFactory.create(
        session=test_session,
        company_id=test_company.id,
        name="Test Branch",
    )

    url_hash = hashlib.sha256(f"http://test/branch/{branch.id}".encode()).hexdigest()
    qr_code = await QRCodeFactory.create(
        session=test_session,
        company_branch_id=branch.id,
        url_hash=url_hash,
        qr_options={"version": 1, "box_size": 10},
    )

    update_data = QRCodeUpdate(qr_options={"version": 2})

    updated_qr_code = await qr_code_service.update_qr_code_by_hash(
        url_hash, update_data
    )

    assert updated_qr_code.id == qr_code.id
    assert updated_qr_code.qr_options == {"version": 2, "box_size": 10}


@pytest.mark.asyncio
async def test_update_qr_code_by_hash_empty_update(
    qr_code_service, test_session: AsyncSession, test_company
):
    branch = await CompanyBranchFactory.create(
        session=test_session,
        company_id=test_company.id,
        name="Test Branch",
    )

    url_hash = hashlib.sha256(f"http://test/branch/{branch.id}".encode()).hexdigest()
    qr_code = await QRCodeFactory.create(
        session=test_session,
        company_branch_id=branch.id,
        url_hash=url_hash,
        qr_options={"version": 1},
    )

    update_data = QRCodeUpdate()

    updated_qr_code = await qr_code_service.update_qr_code_by_hash(
        url_hash, update_data
    )

    assert updated_qr_code.id == qr_code.id
    assert updated_qr_code.qr_options == {"version": 1}


@pytest.mark.asyncio
async def test_update_qr_code_by_hash_not_found(qr_code_service):
    url_hash = hashlib.sha256("http://test/branch/99999".encode()).hexdigest()
    update_data = QRCodeUpdate(qr_options={"version": 2})

    with pytest.raises(NotFoundError) as exc_info:
        await qr_code_service.update_qr_code_by_hash(url_hash, update_data)

    assert "not found" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_create_qr_code_for_branch_success(
    qr_code_service, test_session: AsyncSession, test_company
):
    branch = await CompanyBranchFactory.create(
        session=test_session,
        company_id=test_company.id,
        name="Test Branch",
    )

    qr_options = {"version": 1, "box_size": 10}
    qr_code = await qr_code_service.create_qr_code_for_branch(
        branch.id, qr_options=qr_options
    )

    assert qr_code.id is not None
    assert qr_code.company_branch_id == branch.id
    assert qr_code.qr_options == qr_options
    assert len(qr_code.url_hash) == 64


@pytest.mark.asyncio
async def test_create_qr_code_for_branch_without_options(
    qr_code_service, test_session: AsyncSession, test_company
):
    branch = await CompanyBranchFactory.create(
        session=test_session,
        company_id=test_company.id,
        name="Test Branch",
    )

    qr_code = await qr_code_service.create_qr_code_for_branch(branch.id)

    assert qr_code.id is not None
    assert qr_code.company_branch_id == branch.id
    assert qr_code.qr_options == {}
    assert len(qr_code.url_hash) == 64


@pytest.mark.asyncio
async def test_generate_url_hash():
    data = "http://test/branch/123"
    hash_result = QRCodeService.generate_url_hash(data)

    assert len(hash_result) == 64
    assert hash_result == hashlib.sha256(data.encode()).hexdigest()


@pytest.mark.asyncio
async def test_generate_qr_code_image_bytes(
    qr_code_service, test_session: AsyncSession, test_company
):
    branch = await CompanyBranchFactory.create(
        session=test_session,
        company_id=test_company.id,
        name="Test Branch",
    )

    qr_code = await QRCodeFactory.create(
        session=test_session,
        company_branch_id=branch.id,
    )

    image_bytes = qr_code_service.generate_qr_code_image_bytes(qr_code)

    assert isinstance(image_bytes, bytes)
    assert len(image_bytes) > 0
    assert image_bytes.startswith(b"\x89PNG")


@pytest.mark.asyncio
async def test_generate_qr_code_image_bytes_with_options(
    qr_code_service, test_session: AsyncSession, test_company
):
    branch = await CompanyBranchFactory.create(
        session=test_session,
        company_id=test_company.id,
        name="Test Branch",
    )

    qr_code = await QRCodeFactory.create(
        session=test_session,
        company_branch_id=branch.id,
        qr_options={"version": 1, "box_size": 15, "fill_color": "blue"},
    )

    image_bytes = qr_code_service.generate_qr_code_image_bytes(qr_code)

    assert isinstance(image_bytes, bytes)
    assert len(image_bytes) > 0
    assert image_bytes.startswith(b"\x89PNG")
