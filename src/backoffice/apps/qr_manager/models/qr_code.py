from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import CHAR, CheckConstraint, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.backoffice.models import Base, IdMixin


class QRCode(IdMixin, Base):
    __tablename__ = "qr_codes"

    company_branch_id: Mapped[int] = mapped_column(
        ForeignKey("company_branches.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        unique=True,
    )
    qr_options: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        default=dict,
        nullable=True,
    )
    url_hash: Mapped[str] = mapped_column(
        CHAR(64), nullable=False, unique=True, index=True
    )
    scan_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    last_scanned: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

    # Relationships
    company_branch: Mapped["CompanyBranch"] = relationship(  # type: ignore
        back_populates="qr_code",
    )

    __table_args__ = (
        UniqueConstraint("url_hash", name="uq_qr_codes_url_hash"),
        UniqueConstraint("company_branch_id", name="uq_qr_codes_company_branch_id"),
        CheckConstraint("scan_count >= 0", name="ck_qr_codes_scan_count_nonneg"),
    )
