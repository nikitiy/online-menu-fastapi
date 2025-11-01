from typing import List, Optional

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.backoffice.models import Base, IdMixin


class CompanyBranch(Base, IdMixin):
    __tablename__ = "company_branches"
    __repr_fields__ = ("company_id", "name", "address_id")

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    address_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("addresses.id", ondelete="SET NULL"), nullable=True, index=True
    )
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)

    # External ID for integration
    external_id: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, index=True
    )

    # Relationships
    company: Mapped["Company"] = relationship(  # type: ignore
        back_populates="branches",
    )
    address: Mapped[Optional["Address"]] = relationship("Address")  # type: ignore
    branch_menus: Mapped[List["CompanyBranchMenu"]] = relationship(  # type: ignore
        "CompanyBranchMenu",
        back_populates="company_branch",
        cascade="all, delete-orphan",
    )
    qr_codes: Mapped[List["QRCode"]] = relationship(  # type: ignore
        "QRCode",
        back_populates="company_branch",
        cascade="all, delete-orphan",
    )
