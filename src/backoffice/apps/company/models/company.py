from typing import List, Optional

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.backoffice.apps.company.models.types import (
    CompanyEstablishmentType,
    CompanyRole,
    CuisineCategory,
)
from src.backoffice.models import Base, CreatedUpdatedMixin, IdMixin


class Company(Base, IdMixin, CreatedUpdatedMixin):
    __tablename__ = "companies"
    __repr_fields__ = ("name", "subdomain")

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    subdomain: Mapped[str] = mapped_column(
        String(63),
        unique=True,
        index=True,
    )

    type_of_establishment: Mapped[CompanyEstablishmentType] = mapped_column(
        PGEnum(CompanyEstablishmentType, name="company_establishment_type"),
        default=CompanyEstablishmentType.RESTAURANT,
        nullable=False,
    )

    cuisine_category: Mapped[CuisineCategory] = mapped_column(
        PGEnum(CuisineCategory, name="cuisine_category"),
        default=CuisineCategory.OTHER,
        nullable=False,
    )

    # Relationships
    branches: Mapped[List["CompanyBranch"]] = relationship(  # type: ignore
        back_populates="company",
        cascade="all, delete-orphan",
    )
    members: Mapped[List["CompanyMember"]] = relationship(  # type: ignore
        back_populates="company",
        cascade="all, delete-orphan",
    )
    site: Mapped[Optional["Site"]] = relationship(  # type: ignore
        back_populates="company",
        uselist=False,
        cascade="all, delete-orphan",
    )

    @property
    def owner(self) -> Optional["CompanyMember"]:  # type: ignore
        for member in self.members:
            if member.role == CompanyRole.OWNER:
                return member
        return None
