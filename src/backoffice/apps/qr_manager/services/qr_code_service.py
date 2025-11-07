import hashlib
import io
from typing import Any, Dict, Optional

import qrcode
from qrcode.image.pil import PilImage
from sqlalchemy.ext.asyncio import AsyncSession

from src.backoffice.apps.company.models import CompanyBranch
from src.backoffice.apps.company.services import CompanyBranchService
from src.backoffice.apps.qr_manager.models import QRCode
from src.backoffice.apps.qr_manager.repositories import QRCodeRepository
from src.backoffice.apps.qr_manager.schemas import QRCodeCreate, QRCodeUpdate
from src.backoffice.core.config import auth_settings
from src.backoffice.core.exceptions import NotFoundError


class QRCodeService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = QRCodeRepository(session)
        self.company_branch_service = CompanyBranchService(session)

    async def create_qr_code(self, qr_code_data: QRCodeCreate) -> QRCode:
        await self.company_branch_service.get_branch_by_id_or_raise(
            qr_code_data.company_branch_id
        )

        existing_qr_code = await self.repository.get_by_company_branch_id(
            qr_code_data.company_branch_id
        )
        if existing_qr_code:
            raise ValueError(
                f"QR code already exists for company branch with id '{qr_code_data.company_branch_id}'"
            )

        qr_code = await self.repository.create(
            company_branch_id=qr_code_data.company_branch_id,
            url_hash=qr_code_data.url_hash,
            qr_options=qr_code_data.qr_options or {},
        )

        return qr_code

    async def get_company_branch_by_id(self, company_branch_id: int) -> CompanyBranch:
        return await self.company_branch_service.get_branch_by_id_or_raise(
            company_branch_id
        )

    async def get_qr_code_by_company_branch(self, company_branch_id: int) -> QRCode:
        qr_code = await self.repository.get_by_company_branch_id(company_branch_id)
        if not qr_code:
            raise NotFoundError(
                f"QR code for company branch with id '{company_branch_id}' not found"
            )
        return qr_code

    async def get_company_branch_by_qr_code_hash(self, url_hash: str) -> CompanyBranch:
        qr_code = await self.repository.get_by_url_hash(url_hash)
        if not qr_code:
            raise NotFoundError(f"QR code with hash '{url_hash}' not found")

        return await self.company_branch_service.get_branch_by_id_or_raise(
            qr_code.company_branch_id
        )

    async def update_qr_code_by_hash(
        self, url_hash: str, update_data: QRCodeUpdate
    ) -> QRCode:
        qr_code = await self.repository.get_by_url_hash(url_hash)
        if not qr_code:
            raise NotFoundError(f"QR code with hash '{url_hash}' not found")

        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            return qr_code

        updated_qr_code = await self.repository.update(qr_code.id, **update_dict)
        if not updated_qr_code:
            raise NotFoundError(f"QR code with hash '{url_hash}' not found")

        return updated_qr_code

    def generate_qr_code_image_bytes(self, qr_code: QRCode) -> bytes:
        qr_url = f"{auth_settings.frontend_url}/branch/{qr_code.company_branch_id}"

        qr_image = self._generate_qr_code_image(qr_url, qr_code.qr_options)
        img_buffer = io.BytesIO()
        qr_image.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        return img_buffer.getvalue()

    @staticmethod
    def _generate_qr_code_image(
        data: str, options: Optional[Dict[str, Any]] = None
    ) -> PilImage:
        qr = qrcode.QRCode(
            version=options.get("version", 1) if options else 1,
            error_correction=(
                qrcode.constants.ERROR_CORRECT_L
                if not options or options.get("error_correction") == "L"
                else (
                    qrcode.constants.ERROR_CORRECT_M
                    if options.get("error_correction") == "M"
                    else (
                        qrcode.constants.ERROR_CORRECT_Q
                        if options.get("error_correction") == "Q"
                        else qrcode.constants.ERROR_CORRECT_H
                    )
                )
            ),
            box_size=options.get("box_size", 10) if options else 10,
            border=options.get("border", 4) if options else 4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(
            fill_color=options.get("fill_color", "black") if options else "black",
            back_color=options.get("back_color", "white") if options else "white",
        )

        return img

    async def create_qr_code_for_branch(
        self, company_branch_id: int, qr_options: Optional[Dict[str, Any]] = None
    ) -> QRCode:
        qr_url = f"{auth_settings.frontend_url}/branch/{company_branch_id}"
        url_hash = self.generate_url_hash(qr_url)

        qr_code_data = QRCodeCreate(
            company_branch_id=company_branch_id,
            url_hash=url_hash,
            qr_options=qr_options,
        )
        return await self.create_qr_code(qr_code_data)

    @staticmethod
    def generate_url_hash(data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()
