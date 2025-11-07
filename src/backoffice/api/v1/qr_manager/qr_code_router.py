from fastapi import APIRouter
from fastapi.responses import Response

from src.backoffice.apps.qr_manager.schemas import QRCodeResponse, QRCodeUpdate
from src.backoffice.core.dependencies import AuthenticatedUserDep, QRCodeApplicationDep

router = APIRouter(prefix="/qr-codes", tags=["qr-codes"])


@router.get(
    "/branch/{company_branch_id}",
    response_model=QRCodeResponse,
    summary="Get QR code by company branch",
)
async def get_qr_code_by_branch(
    company_branch_id: int,
    request_user: AuthenticatedUserDep,
    application: QRCodeApplicationDep,
):
    """Get QR code for a company branch"""
    return await application.get_qr_code_by_company_branch(
        company_branch_id, request_user.id
    )


@router.get(
    "/branch/{company_branch_id}/image",
    response_class=Response,
    summary="Get QR code image",
)
async def get_qr_code_image(
    company_branch_id: int,
    request_user: AuthenticatedUserDep,
    application: QRCodeApplicationDep,
):
    """Get QR code image as PNG"""
    qr_code = await application.get_qr_code_by_company_branch(
        company_branch_id, request_user.id
    )
    qr_image_bytes = application.qr_code_service.generate_qr_code_image_bytes(qr_code)
    return Response(content=qr_image_bytes, media_type="image/png")


@router.put(
    "/{url_hash}",
    response_model=QRCodeResponse,
    summary="Update QR code",
)
async def update_qr_code(
    url_hash: str,
    update_data: QRCodeUpdate,
    request_user: AuthenticatedUserDep,
    application: QRCodeApplicationDep,
):
    """Update QR code"""
    return await application.update_qr_code_by_hash(
        url_hash, update_data, request_user.id
    )
