from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.qr_manager.models import QRCode
from src.backoffice.apps.qr_manager.schemas import QRCodeUpdate
from src.backoffice.apps.qr_manager.services import QRCodeService
from src.backoffice.core.access.access_control import CompanyAccessControl
from src.backoffice.core.access.permissions import (
    QRCodePermission,
    check_qr_code_permission,
)


class QRCodeApplication:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.qr_code_service = QRCodeService(session)
        self.access_control = CompanyAccessControl(session)

    async def get_qr_code_by_company_branch(
        self, company_branch_id: int, user_id: int
    ) -> QRCode:
        company_branch = await self.qr_code_service.get_company_branch_by_id(
            company_branch_id
        )

        await self.access_control.check_company_permission(
            company_id=company_branch.company_id,
            user_id=user_id,
            permission=QRCodePermission.READ,
            permission_checker=check_qr_code_permission,
        )

        return await self.qr_code_service.get_qr_code_by_company_branch(
            company_branch_id
        )

    async def update_qr_code_by_hash(
        self, url_hash: str, update_data: QRCodeUpdate, user_id: int
    ) -> QRCode:
        company_branch = await self.qr_code_service.get_company_branch_by_qr_code_hash(
            url_hash
        )

        await self.access_control.check_company_permission(
            company_id=company_branch.company_id,
            user_id=user_id,
            permission=QRCodePermission.UPDATE,
            permission_checker=check_qr_code_permission,
        )

        updated_qr_code = await self.qr_code_service.update_qr_code_by_hash(
            url_hash, update_data
        )
        await self.session.commit()
        return updated_qr_code
