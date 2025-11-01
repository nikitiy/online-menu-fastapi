from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.backoffice.models import Base, IdMixin


class CompanyBranchMenu(Base, IdMixin):
    __tablename__ = "company_branches_menus"

    company_branch_id: Mapped[int] = mapped_column(
        ForeignKey("company_branches.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    menu_item_id: Mapped[int] = mapped_column(
        ForeignKey("menu_items.id", ondelete="CASCADE"), index=True, nullable=False
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    available: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    company_branch: Mapped["CompanyBranch"] = relationship(  # type: ignore
        back_populates="branch_menus",
    )
    menu_item: Mapped["MenuItem"] = relationship(  # type: ignore
        back_populates="branch_menus",
    )
