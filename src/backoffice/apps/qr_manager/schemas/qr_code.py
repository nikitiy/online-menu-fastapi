from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class QRCodeBase(BaseModel):
    """Basic QR code schema"""

    qr_options: Optional[Dict[str, Any]] = Field(
        None, description="QR code generation options"
    )


class QRCodeCreate(QRCodeBase):
    """Create QR code schema"""

    company_branch_id: int = Field(..., description="Company branch ID")
    url_hash: str = Field(..., min_length=64, max_length=64, description="URL hash")


class QRCodeUpdate(BaseModel):
    """Update QR code schema"""

    qr_options: Optional[Dict[str, Any]] = Field(
        None, description="QR code generation options"
    )


class QRCodeInDB(QRCodeBase):
    """QR code in the database schema"""

    id: int
    company_branch_id: int
    url_hash: str
    scan_count: int
    last_scanned: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QRCodeResponse(QRCodeInDB):
    """QR code response schema"""

    pass
