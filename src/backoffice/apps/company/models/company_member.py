from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.backoffice.apps.company.models.types import CompanyRole
from src.backoffice.models import Base, CreatedUpdatedMixin, IdMixin


class CompanyMember(Base, IdMixin, CreatedUpdatedMixin):
    __tablename__ = "company_members"
    __repr_fields__ = ("company_id", "user_id", "role")

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[CompanyRole] = mapped_column(
        PGEnum(CompanyRole, name="company_role"),
        nullable=False,
        default=CompanyRole.VIEWER,
    )

    # Relationships
    company: Mapped["Company"] = relationship(  # type: ignore
        "Company", back_populates="members"
    )
    user: Mapped["User"] = relationship(  # type: ignore
        "User", back_populates="company_memberships"
    )

    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "user_id",
            name="uq_company_member_company_user",
        ),
        Index(
            "uq_company_member_company_role_owner",
            "company_id",
            "role",
            unique=True,
            postgresql_where="role = 'OWNER'",
        ),
    )
